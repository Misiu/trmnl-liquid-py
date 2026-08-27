"""Filters ported from usetrmnl/trmnl-liquid 0.8.2.

The functions in this module intentionally mimic Ruby behavior where it differs
from idiomatic Python. Rails/I18n-backed behavior is out of scope for the first
compatibility target; fallback behavior is implemented instead.
"""

from __future__ import annotations

import html
import json as _json
import re
import secrets
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import mistune
from dateutil import parser as date_parser
from liquid import Token, TokenStream
from liquid.builtin.expressions import BooleanExpression, tokenize
from liquid.filter import with_context
from liquid.token import TOKEN_EXPRESSION

from .qr import render_qr_svg
from .ruby_values import ruby_wrap

if TYPE_CHECKING:
    from liquid.context import RenderContext

_NUMERIC = re.compile(r"^-?\d+(?:\.\d+)?$")
_TO_I = re.compile(r"^[\s]*([+-]?\d+)")
_MARKDOWN_BLOCK_TYPES = frozenset(
    {
        "block_code",
        "block_error",
        "block_html",
        "block_quote",
        "footnote_def",
        "footnotes",
        "heading",
        "list",
        "paragraph",
        "table",
        "thematic_break",
    }
)


class _RedcarpetLikeRenderer(mistune.HTMLRenderer):
    """Use Redcarpet-compatible output for the supported Markdown surface."""

    def text(self, text: str) -> str:
        return html.escape(text, quote=True).replace("&#x27;", "&#39;")

    def render_tokens(self, tokens: Iterable[dict[str, Any]], state: Any) -> str:
        parts: list[str] = []
        has_output = False
        for token in tokens:
            rendered = self.render_token(token, state)
            if not rendered:
                continue
            if has_output and token.get("type") in _MARKDOWN_BLOCK_TYPES:
                parts.append("\n")
            parts.append(rendered)
            has_output = True
        return "".join(parts)

    def thematic_break(self) -> str:
        return "<hr>\n"

    def block_code(self, code: str, info: str | None = None) -> str:
        if code and not code.endswith("\n"):
            code += "\n"
        return super().block_code(code, info)


_MARKDOWN = mistune.create_markdown(renderer=_RedcarpetLikeRenderer())


def ruby_to_i(value: object) -> int:
    """Approximate Ruby's String#to_i semantics used by trmnl-liquid."""
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    match = _TO_I.match(str(value))
    return int(match.group(1)) if match else 0


def append_random(value: object) -> str:
    return f"{'' if value is None else value}{secrets.token_hex(2)}"


def days_ago(value: object, timezone: str = "Etc/UTC") -> date:
    today = datetime.now(ZoneInfo(timezone)).date()
    return today - timedelta(days=ruby_to_i(value))


def group_by(collection: Iterable[object], key: str) -> object:
    result: dict[object, list[object]] = {}
    for item in collection:
        group = item.get(key) if isinstance(item, Mapping) else None
        result.setdefault(group, []).append(ruby_wrap(item))
    return ruby_wrap(result)


def find_by(
    collection: Iterable[object], key: str, value: object, fallback: object = None
) -> object:
    for item in collection:
        if isinstance(item, Mapping) and item.get(key) == value:
            return ruby_wrap(item)
    return fallback


def markdown_to_html(markdown: object) -> str:
    value = "" if markdown is None else str(markdown)
    return str(_MARKDOWN(value))


def number_with_delimiter(
    number: object, delimiter: str = ",", separator: str = "."
) -> str:
    value = "" if number is None else str(number)
    if not _NUMERIC.fullmatch(value):
        return value

    integer, dot, fractional = value.partition(".")
    negative = integer.startswith("-")
    if negative:
        integer = integer[1:]
    chunks: list[str] = []
    while integer:
        chunks.append(integer[-3:])
        integer = integer[:-3]
    grouped = delimiter.join(reversed(chunks))
    if negative:
        grouped = f"-{grouped}"
    return f"{grouped}{separator}{fractional}" if dot else grouped


def number_to_currency(
    number: object,
    unit_or_locale: str = "$",
    delimiter: str = ",",
    separator: str = ".",
    precision: int = 2,
) -> str:
    result = number_with_delimiter(number, delimiter, separator)
    dollars, _, cents = result.partition(separator)
    if precision <= 0:
        return f"{unit_or_locale}{dollars}"
    cents = cents[:precision].ljust(precision, "0")
    return f"{unit_or_locale}{dollars}{separator}{cents}"


def l_word(word: object, locale: str) -> str:
    del locale
    return f"custom_plugins.{word}"


def l_date(value: object, format: str, locale: str = "en") -> str:
    del format, locale
    return "" if value is None else str(value)


def map_to_i(collection: Iterable[object]) -> list[int]:
    return [ruby_to_i(item) for item in collection]


def pluralize(
    singular: str,
    count: object,
    *,
    plural: object | None = None,
    locale: object | None = None,
) -> str:
    del locale
    plural_word = str(plural) if plural is not None else f"{singular}s"
    return f"1 {singular}" if count == 1 else f"{count} {plural_word}"


def json(value: object) -> str:
    return _json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_json(value: object) -> Any:
    return ruby_wrap(_json.loads(str(value)))


def sample(array: list[Any]) -> Any:
    return secrets.choice(array) if array else None


@with_context
def where_exp(
    input: object,
    variable: object,
    expression: object,
    *,
    context: RenderContext,
) -> object:
    """Select values using Liquid's own logical-expression parser."""
    if isinstance(input, Mapping):
        items: Iterable[object] = input.values()
    elif isinstance(input, (list, tuple, range)):
        items = input
    else:
        return input

    source = str(expression)
    token = Token(TOKEN_EXPRESSION, source, 0, source)
    condition = BooleanExpression.parse(
        context.env, TokenStream(tokenize(source, parent_token=token))
    )

    selected: list[object] = []
    name = str(variable)
    for item in items:
        with context.extend({name: item}):
            if condition.evaluate(context):
                selected.append(ruby_wrap(item))
    return selected


def ordinalize_number(number: int) -> str:
    if 11 <= number % 100 <= 13:
        return f"{number}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _to_time(value: object) -> datetime:
    if value in ("now", "today"):
        return datetime.now()
    if type(value) is int:
        return datetime.fromtimestamp(value)
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return date_parser.parse(str(value))


def ordinalize(value: object, strftime_format: object) -> str:
    time = _to_time(value)
    formatted = str(strftime_format).replace(
        "<<ordinal_day>>", ordinalize_number(time.day)
    )
    return time.strftime(formatted)


def qr_code(
    data: object,
    size: int = 11,
    level: object = "",
    view: object = "responsive",
) -> str:
    return render_qr_svg(data, size=size, level=level, view=view)
