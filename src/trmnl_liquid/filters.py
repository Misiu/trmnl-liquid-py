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
import qrcode
from dateutil import parser as date_parser
from liquid import Token, TokenStream
from liquid.builtin.expressions import BooleanExpression, tokenize
from liquid.filter import with_context
from liquid.token import TOKEN_EXPRESSION
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

from .ruby_values import ruby_wrap

if TYPE_CHECKING:
    from liquid.context import RenderContext

_NUMERIC = re.compile(r"^-?\d+(?:\.\d+)?$")
_TO_I = re.compile(r"^[\s]*([+-]?\d+)")


class _RedcarpetLikeRenderer(mistune.HTMLRenderer):
    """Use Redcarpet-compatible output for the supported Markdown surface."""

    def text(self, text: str) -> str:
        return html.escape(text, quote=True).replace("&#x27;", "&#39;")

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        return super().heading(text, level, **attrs) + "\n"


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


Edge = tuple[int, int, int]


def _qr_path(modules: list[list[bool]]) -> str:
    dir_up, dir_down, dir_left, dir_right = range(4)
    deltas = ((0, -1), (0, 1), (-1, 0), (1, 0))
    commands = ("v-", "v", "h-", "h")

    module_count = len(modules)
    matrix_size = module_count + 1
    edge_matrix: list[list[list[Edge] | None]] = [
        [None for _ in range(matrix_size)] for _ in range(matrix_size)
    ]
    edge_count = 0

    def add_edge(x: int, y: int, direction: int) -> None:
        nonlocal edge_count
        cell = edge_matrix[y][x]
        if cell is None:
            cell = []
            edge_matrix[y][x] = cell
        cell.append((x, y, direction))
        edge_count += 1

    for row_index in range(module_count + 1):
        for col_index in range(module_count):
            above = row_index > 0 and modules[row_index - 1][col_index]
            below = row_index < module_count and modules[row_index][col_index]
            if above and not below:
                add_edge(col_index + 1, row_index, dir_left)
            elif not above and below:
                add_edge(col_index, row_index, dir_right)

    for row_index in range(module_count):
        for col_index in range(module_count + 1):
            left = col_index > 0 and modules[row_index][col_index - 1]
            right = col_index < module_count and modules[row_index][col_index]
            if left and not right:
                add_edge(col_index, row_index, dir_down)
            elif not left and right:
                add_edge(col_index, row_index + 1, dir_up)

    path_parts: list[str] = []
    search_y = 0
    search_x = 0

    while edge_count > 0:
        start_edge: Edge | None = None
        found_y = search_y
        found_x = search_x
        for y in range(search_y, matrix_size):
            start_col = search_x if y == search_y else 0
            for x in range(start_col, matrix_size):
                cell = edge_matrix[y][x]
                if cell:
                    start_edge = cell[0]
                    found_y = y
                    found_x = x
                    break
            if start_edge is not None:
                break

        if start_edge is None:
            break

        search_y = found_y
        search_x = found_x
        path = f"M{start_edge[0]} {start_edge[1]}"
        current_edge: Edge | None = start_edge
        current_dir: int | None = None
        current_count = 0

        while current_edge is not None:
            x, y, direction = current_edge
            cell = edge_matrix[y][x]
            assert cell is not None
            cell.remove(current_edge)
            if not cell:
                edge_matrix[y][x] = None
            edge_count -= 1

            if direction == current_dir:
                current_count += 1
            else:
                if current_dir is not None:
                    path += commands[current_dir] + str(current_count)
                current_dir = direction
                current_count = 1

            dx, dy = deltas[direction]
            next_cell = edge_matrix[y + dy][x + dx]
            current_edge = next_cell[0] if next_cell else None

        path_parts.append(path + "z")

    return "".join(path_parts)


def qr_code(
    data: object,
    size: int = 11,
    level: object = "",
    view: object = "responsive",
) -> str:
    level_name = str(level).lower()
    if level_name not in {"l", "m", "q", "h"}:
        level_name = "h"

    correction = {
        "l": ERROR_CORRECT_L,
        "m": ERROR_CORRECT_M,
        "q": ERROR_CORRECT_Q,
        "h": ERROR_CORRECT_H,
    }[level_name]

    qr = qrcode.QRCode(
        version=None,
        error_correction=correction,
        box_size=1,
        border=0,
    )
    qr.add_data(str(data))
    qr.make(fit=True)
    modules = [[bool(cell) for cell in row] for row in qr.get_matrix()]

    module_size = int(size)
    width = len(modules) * module_size
    height = width
    if str(view) == "responsive":
        dimensions = f'viewBox="0 0 {width} {height}"'
    else:
        dimensions = f'width="{width}" height="{height}"'

    attributes = " ".join(
        (
            'version="1.1"',
            'xmlns="http://www.w3.org/2000/svg"',
            'xmlns:xlink="http://www.w3.org/1999/xlink"',
            'xmlns:ev="http://www.w3.org/2001/xml-events"',
            dimensions,
            'shape-rendering="crispEdges"',
            'class="qr-code"',
        )
    )
    dimension = max(width, height)
    background = (
        f'<rect width="{dimension}" height="{dimension}" x="0" y="0" fill="#fff"/>'
    )
    path = (
        f'<path d="{_qr_path(modules)}" fill="#000" '
        f'transform="translate(0,0) scale({module_size})"/>'
    )
    return (
        '<?xml version="1.0" standalone="yes"?>'
        f"<svg {attributes}>{background}{path}</svg>"
    )
