"""TRMNL's inline ``{% template %}`` block tag.

TRMNL's Ruby implementation stores the template body as raw Liquid source and
only strips leading/trailing whitespace. It does not parse and reconstruct the
body while defining the template. This matters for source fidelity and for Liquid
syntax whose textual form is significant.

References:
- TRMNL Liquid 0.8.2 TemplateTag:
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/template_tag.rb
- Ruby Liquid 5.13 tokenizer (TemplateTag receives raw token strings):
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/tokenizer.rb
- python-liquid 2.3.1 lexer/token source positions:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/lex.py
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/token.py
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, TextIO

from liquid.ast import Node
from liquid.exceptions import LiquidSyntaxError
from liquid.tag import Tag
from liquid.token import TOKEN_EOF, TOKEN_EXPRESSION, TOKEN_TAG, Token

from .memory_system import MemorySystem

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.stream import TokenStream

TAG_TEMPLATE = "template"
TAG_ENDTEMPLATE = "endtemplate"
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_/]+$")


def _body_start(token: Token, tag_end: str) -> int:
    """Return the first source index after the opening template tag."""
    index = token.source.find(tag_end, token.start_index)
    if index < 0:
        raise LiquidSyntaxError("expected template tag terminator", token=token)
    return index + len(tag_end)


def _tag_start(token: Token, tag_start: str) -> int:
    """Return the source index of the tag delimiter for a parsed tag token."""
    index = token.source.rfind(tag_start, 0, token.start_index + 1)
    if index < 0:
        raise LiquidSyntaxError("expected tag start", token=token)
    return index


def _tag_end(token: Token, tag_end: str) -> int:
    """Return the source index immediately after a parsed tag token."""
    index = token.source.find(tag_end, token.start_index)
    if index < 0:
        raise LiquidSyntaxError("expected tag terminator", token=token)
    return index + len(tag_end)


def _is_literal_endtemplate(token: Token, tag_start: str, tag_end: str) -> bool:
    """Match the exact terminator recognized by TRMNL Liquid 0.8.2.

    TRMNL's Ruby ``TemplateTag#parse`` stops only when ``token.strip`` equals
    ``"{% endtemplate %}"``. Whitespace-control variants such as
    ``"{%- endtemplate -%}"`` are therefore part of the captured template body and
    do not close the definition.

    Ruby reference:
    https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/template_tag.rb
    """
    start = _tag_start(token, tag_start)
    end = _tag_end(token, tag_end)
    return token.source[start:end].strip() == "{% endtemplate %}"


class TemplateNode(Node):
    """Register an inline template when this node is rendered."""

    __slots__ = ("body", "name")

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
        """Capture the template body without parsing or reconstructing its source.

        Ruby TRMNL's TemplateTag appends tokenizer strings verbatim until a token
        whose stripped source is exactly ``{% endtemplate %}``, then calls ``strip``.
        python-liquid exposes source text and positions on tokens, so we preserve the
        same semantics by slicing the original source and advancing the public
        ``TokenStream``.

        Ruby reference:
        https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/template_tag.rb
        Python references:
        https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/lex.py
        https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/stream.py
        """
        token = stream.eat(TOKEN_TAG)
        if stream.current.kind == TOKEN_EXPRESSION:
            name = stream.eat(TOKEN_EXPRESSION).value.strip()
        else:
            name = ""

        start = _body_start(token, self.env.tag_end_string)
        while stream.current.kind != TOKEN_EOF:
            if (
                stream.current.kind == TOKEN_TAG
                and stream.current.value == TAG_ENDTEMPLATE
                and _is_literal_endtemplate(
                    stream.current,
                    self.env.tag_start_string,
                    self.env.tag_end_string,
                )
            ):
                closing = stream.current
                end = _tag_start(closing, self.env.tag_start_string)
                return self.node_class(token, name, token.source[start:end].strip())
            next(stream)

        # TRMNL 0.8.2's custom block consumes the remaining tokenizer input when no
        # exact closing token exists; it does not ask Liquid::Block to raise a missing
        # end-tag error. Mirror that behavior by capturing through EOF.
        return self.node_class(token, name, token.source[start:].strip())
