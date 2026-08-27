"""TRMNL's inline ``{% template %}`` block tag."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING
from typing import TextIO

from liquid.ast import BlockNode, Node
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF, TOKEN_EXPRESSION, TOKEN_TAG, Token

from .memory_system import MemorySystem

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.stream import TokenStream

TAG_TEMPLATE = "template"
TAG_ENDTEMPLATE = "endtemplate"
ENDTEMPLATEBLOCK = frozenset((TAG_ENDTEMPLATE, TOKEN_EOF))
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_/]+$")


class TemplateNode(Node):
    """Register an inline template when this node is rendered."""

    __slots__ = ("name", "body")

    def __init__(self, token: Token, name: str, body: str) -> None:
        super().__init__(token)
        self.name = name
        self.body = body

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        if not NAME_PATTERN.fullmatch(self.name):
            inspected = json.dumps(self.name, ensure_ascii=False)
            return buffer.write(
                f"Liquid error: invalid template name {inspected} - template names "
                "must contain only letters, numbers, underscores, and slashes"
            )

        loader = context.env.loader
        if isinstance(loader, MemorySystem):
            loader.register(self.name, self.body)
        return 0


class TemplateTag(Tag):
    """Define a named template for later use by Liquid's ``render`` tag."""

    name = TAG_TEMPLATE
    end = TAG_ENDTEMPLATE
    block = True
    node_class = TemplateNode

    def parse(self, stream: TokenStream) -> TemplateNode:
        token = stream.eat(TOKEN_TAG)
        if stream.current.kind == TOKEN_EXPRESSION:
            name = stream.eat(TOKEN_EXPRESSION).value.strip()
        else:
            name = ""

        block: BlockNode = get_parser(self.env).parse_block(stream, ENDTEMPLATEBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDTEMPLATE)
        return self.node_class(token, name, str(block).strip())
