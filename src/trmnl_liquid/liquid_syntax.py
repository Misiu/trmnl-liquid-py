"""Ruby Liquid lax filter-syntax compatibility for python-liquid.

Ruby Liquid 5.13 in lax mode accepts a comma as the separator between a filter
name and its first argument (for example ``| append, "b"``). TRMNL Liquid 0.8.2
uses Ruby Liquid's default lax mode and its own QR specs exercise that syntax.
python-liquid 2.3.1 tokenizes the comma correctly, but ``Filter.parse`` only starts
an argument list after a colon.

This module adapts expression *tokens*, not template source text. Only a comma
immediately following ``| <filter-name>`` is reclassified as a colon; all parsing,
validation and evaluation remain python-liquid's implementation.

References:
- Ruby Liquid 5.13 lax variable/filter parser:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/variable.rb
- TRMNL Liquid 0.8.2 environment (Ruby Liquid lax mode by default):
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid.rb
- python-liquid 2.3.1 filter parser:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/expressions/filtered.py
- python-liquid 2.3.1 expression tokenizer:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/expressions/_tokenize.py
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

from liquid.builtin.expressions import (
    FilteredExpression,
    Nil,
    parse_identifier,
    tokenize,
)
from liquid.builtin.output import OutputNode
from liquid.builtin.tags.assign_tag import AssignNode, TAG_ASSIGN
from liquid.builtin.tags.echo_tag import EchoNode, TAG_ECHO
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import (
    TOKEN_ASSIGN,
    TOKEN_COLON,
    TOKEN_COMMA,
    TOKEN_EOF,
    TOKEN_EXPRESSION,
    TOKEN_OUTPUT,
    TOKEN_PIPE,
    TOKEN_TAG,
    TOKEN_WORD,
    Token,
)

if TYPE_CHECKING:
    from liquid.environment import Environment


def _ruby_lax_filter_tokens(tokens: Iterable[Token]) -> Iterator[Token]:
    """Adapt Ruby lax ``| filter, arg`` tokens for python-liquid's parser.

    Ruby reference:
    https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/variable.rb
    Python reference:
    https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/expressions/filtered.py
    """
    after_pipe = False
    after_filter_name = False

    for original in tokens:
        token = original
        if after_filter_name and original.kind == TOKEN_COMMA:
            token = Token(
                TOKEN_COLON,
                ":",
                start_index=original.start_index,
                source=original.source,
            )

        yield token

        if token.kind == TOKEN_PIPE:
            after_pipe = True
            after_filter_name = False
        elif after_pipe and token.kind == TOKEN_WORD:
            after_pipe = False
            after_filter_name = True
        else:
            after_pipe = False
            after_filter_name = False


def _expression_stream(token: Token) -> TokenStream:
    """Tokenize an expression and apply only Ruby Liquid lax filter syntax."""
    return TokenStream(_ruby_lax_filter_tokens(tokenize(token.value, token)))


def _parse_filtered_expression(env: Environment, token: Token) -> Expression:
    """Delegate parsing to python-liquid after adapting Ruby lax filter tokens."""
    return FilteredExpression.parse(env, _expression_stream(token))


class RubyLaxOutput(Tag):
    """Output parser using Ruby Liquid's lax leading-comma filter syntax.

    The implementation mirrors python-liquid's built-in ``Output.parse`` and only
    changes the token stream passed to ``FilteredExpression.parse``.

    Python reference:
    https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/output.py
    """

    name = TOKEN_OUTPUT
    block = False
    node_class = OutputNode

    def parse(self, stream: TokenStream) -> OutputNode:
        token = stream.eat(TOKEN_OUTPUT)
        expression_token = stream.expect(TOKEN_EXPRESSION)
        return self.node_class(
            token,
            _parse_filtered_expression(self.env, expression_token),
        )


class RubyLaxAssignTag(Tag):
    """Assign parser using Ruby Liquid's lax leading-comma filter syntax.

    Python reference:
    https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/assign_tag.py
    """

    name = TAG_ASSIGN
    block = False
    node_class = AssignNode

    def parse(self, stream: TokenStream) -> AssignNode:
        token = stream.eat(TOKEN_TAG)
        expression_token = stream.expect(TOKEN_EXPRESSION)
        tokens = _expression_stream(expression_token)
        name = parse_identifier(self.env, tokens, allow_trailing_question_mark=False)
        tokens.eat(TOKEN_ASSIGN)
        return self.node_class(
            token,
            name=name,
            expression=FilteredExpression.parse(self.env, tokens),
        )


class RubyLaxEchoTag(Tag):
    """Echo parser using Ruby Liquid's lax leading-comma filter syntax.

    Python reference:
    https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/tags/echo_tag.py
    """

    name = TAG_ECHO
    block = False
    node_class = EchoNode

    def parse(self, stream: TokenStream) -> EchoNode:
        token = stream.eat(TOKEN_TAG)
        if stream.current.kind == TOKEN_EOF:
            expression: Expression = Nil(stream.current)
        else:
            expression_token = stream.expect(TOKEN_EXPRESSION)
            expression = _parse_filtered_expression(self.env, expression_token)
        return self.node_class(token, expression)
