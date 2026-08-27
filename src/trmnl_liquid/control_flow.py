"""Ruby-compatible nested control-flow nodes for python-liquid.

Ruby Liquid rescues runtime errors per child node in every ``BlockBody``. We keep
python-liquid's public ``IfTag`` and ``ForTag`` parsers and adapt only their parsed
child blocks to :class:`TRMNLBlockNode`.

References:
- Ruby Liquid 5.13 BlockBody rendering:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/block_body.rb
- python-liquid 2.3.1 IfTag/IfNode:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/if_tag.py
- python-liquid 2.3.1 ForTag/ForNode:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/for_tag.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from liquid.ast import BlockNode, ConditionalBlockNode, Node
from liquid.builtin.expressions import LoopExpression
from liquid.builtin.tags.for_tag import ForNode, ForTag
from liquid.builtin.tags.if_tag import IfNode, IfTag
from liquid.expression import Expression
from liquid.token import Token

from .template import TRMNLBlockNode

if TYPE_CHECKING:
    from liquid.stream import TokenStream


def _block(block: BlockNode) -> TRMNLBlockNode:
    return TRMNLBlockNode(block.token, block.nodes)


def _optional_block(block: BlockNode | None) -> TRMNLBlockNode | None:
    return _block(block) if block is not None else None


class TRMNLIfNode(IfNode):
    """IfNode whose branch bodies continue after individual runtime errors."""

    def __init__(
        self,
        token: Token,
        condition: Expression,
        consequence: BlockNode,
        alternatives: list[ConditionalBlockNode],
        default: BlockNode | None,
    ) -> None:
        wrapped_alternatives = [
            ConditionalBlockNode(
                alternative.token,
                expression=alternative.expression,
                block=_block(alternative.block),
            )
            for alternative in alternatives
        ]
        super().__init__(
            token=token,
            condition=condition,
            consequence=_block(consequence),
            alternatives=wrapped_alternatives,
            default=_optional_block(default),
        )

    @classmethod
    def from_upstream(cls, node: IfNode) -> TRMNLIfNode:
        """Wrap an upstream IfNode without changing its parsed expressions."""
        return cls(
            token=node.token,
            condition=node.condition,
            consequence=node.consequence,
            alternatives=node.alternatives,
            default=node.default,
        )


class TRMNLIfTag(IfTag):
    """Built-in ``if`` parser with TRMNL's nested block runtime semantics."""

    def parse(self, stream: TokenStream) -> Node:
        node = super().parse(stream)
        if not isinstance(node, IfNode):
            return node
        return TRMNLIfNode.from_upstream(node)


class TRMNLForNode(ForNode):
    """ForNode whose iteration body continues after individual runtime errors."""

    def __init__(
        self,
        token: Token,
        expression: LoopExpression,
        block: BlockNode,
        default: BlockNode | None = None,
    ) -> None:
        super().__init__(
            token=token,
            expression=expression,
            block=_block(block),
            default=_optional_block(default),
        )

    @classmethod
    def from_upstream(cls, node: ForNode) -> TRMNLForNode:
        """Wrap an upstream ForNode without changing its parsed expression."""
        return cls(
            token=node.token,
            expression=node.expression,
            block=node.block,
            default=node.default,
        )


class TRMNLForTag(ForTag):
    """Built-in ``for`` parser with TRMNL's nested block runtime semantics."""

    def parse(self, stream: TokenStream) -> Node:
        node = super().parse(stream)
        if not isinstance(node, ForNode):
            return node
        return TRMNLForNode.from_upstream(node)
