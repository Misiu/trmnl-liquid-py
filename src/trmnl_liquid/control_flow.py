"""Ruby-compatible nested control-flow nodes for python-liquid.

Ruby Liquid rescues runtime errors per child node in every ``BlockBody``. The
python-liquid built-in ``if`` and ``for`` parsers expose ``node_class`` as their
replacement point, so TRMNL can preserve the upstream parsing rules while wrapping
only the parsed child blocks with :class:`TRMNLBlockNode`.

References:
- Ruby Liquid 5.13 BlockBody rendering:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/block_body.rb
- python-liquid 2.3.1 IfTag/IfNode:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/if_tag.py
- python-liquid 2.3.1 ForTag/ForNode:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/for_tag.py
"""

from __future__ import annotations

from liquid.ast import BlockNode, ConditionalBlockNode
from liquid.builtin.expressions import BooleanExpression, LoopExpression
from liquid.builtin.tags.for_tag import ForNode, ForTag
from liquid.builtin.tags.if_tag import IfNode, IfTag
from liquid.token import Token

from .template import TRMNLBlockNode


def _block(block: BlockNode) -> TRMNLBlockNode:
    return TRMNLBlockNode(block.token, block.nodes)


def _optional_block(block: BlockNode | None) -> TRMNLBlockNode | None:
    return _block(block) if block is not None else None


class TRMNLIfNode(IfNode):
    """IfNode whose branch bodies continue after individual runtime errors."""

    def __init__(
        self,
        token: Token,
        condition: BooleanExpression,
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


class TRMNLIfTag(IfTag):
    """Built-in ``if`` parser with TRMNL's nested block runtime semantics."""

    node_class = TRMNLIfNode


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


class TRMNLForTag(ForTag):
    """Built-in ``for`` parser with TRMNL's nested block runtime semantics."""

    node_class = TRMNLForNode
