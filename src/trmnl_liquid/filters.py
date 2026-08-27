"""Filters ported from usetrmnl/trmnl-liquid 0.8.2.

The functions in this module intentionally mimic Ruby behavior where it differs
from idiomatic Python. Rails/I18n-backed behavior is out of scope for the first
compatibility target; fallback behavior is implemented instead.
"""

from __future__ import annotations

import json as _json
import re
import secrets
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

_NUMERIC = re.compile(r"^-?\d+(?:\.\d+)?$")
_TO_I = re.compile(r"^[\s]*([+-]?\d+)")


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


def days_ago(value: object, timezone: str = "Etc/UTC") -> str:
    today = datetime.now(ZoneInfo(timezone)).date()
    return str(today - timedelta(days=ruby_to_i(value)))


def group_by(collection: Iterable[object], key: str) -> dict[object, list[object]]:
    result: dict[object, list[object]] = {}
    for item in collection:
        group = item.get(key) if isinstance(item, Mapping) else None
        result.setdefault(group, []).append(item)
    return result


def find_by(
    collection: Iterable[object], key: str, value: object, fallback: object = None
) -> object:
    for item in collection:
        if isinstance(item, Mapping) and item.get(key) == value:
            return item
    return fallback


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
    numeric_count = ruby_to_i(count)
    return f"1 {singular}" if numeric_count == 1 else f"{count} {plural_word}"


def json(value: object) -> str:
    return _json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_json(value: object) -> Any:
    return _json.loads(str(value))


def sample(array: list[Any]) -> Any:
    return secrets.choice(array)


def ordinalize_number(number: int) -> str:
    if 11 <= number % 100 <= 13:
        return f"{number}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"
