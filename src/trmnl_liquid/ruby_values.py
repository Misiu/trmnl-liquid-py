"""Ruby-style value wrappers used for Liquid output compatibility.

Ruby Liquid 5.13 has explicit Hash/Array inspection helpers and Ruby strings use
``String#inspect`` escaping rules. python-liquid 2.3.1 delegates arbitrary object
output to Python's ``str()``, so mappings returned by TRMNL filters need a small
host-language compatibility layer.

References:
- Ruby Liquid 5.13 Hash/Array inspection:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/utils.rb
- Ruby 4.0.6 String#inspect implementation:
  https://github.com/ruby/ruby/blob/03b6d3f889/string.c
- Ruby 4.0.6 String#inspect documentation:
  https://github.com/ruby/ruby/blob/03b6d3f889/doc/string/inspect.rdoc
- python-liquid 2.3.1 output stringification:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/stringify.py
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_SPECIAL_STRING_ESCAPES = {
    0x07: "a",  # BEL
    0x08: "b",  # BS
    0x09: "t",  # TAB
    0x0A: "n",  # LF
    0x0B: "v",  # VT
    0x0C: "f",  # FF
    0x0D: "r",  # CR
    0x1B: "e",  # ESC
}


class RubyHash(dict[Any, Any]):
    """A dict whose string representation matches Ruby Hash inspection."""

    def __str__(self) -> str:
        return ruby_inspect(self)

    def __repr__(self) -> str:
        return ruby_inspect(self)


def _ruby_string_inspect(value: str) -> str:
    """Render a Python Unicode string like Ruby UTF-8 ``String#inspect``.

    Ruby escapes interpolation markers, C0/DEL controls and Unicode line/paragraph
    separators in addition to quotes and backslashes. The special short escapes are
    defined by Ruby itself rather than JSON conventions.

    References:
    https://github.com/ruby/ruby/blob/03b6d3f889/string.c
    https://github.com/ruby/ruby/blob/03b6d3f889/doc/string/inspect.rdoc
    """
    parts = ['"']
    length = len(value)

    for index, character in enumerate(value):
        codepoint = ord(character)

        if character in {'"', "\\"}:
            parts.append("\\" + character)
            continue

        escape = _SPECIAL_STRING_ESCAPES.get(codepoint)
        if escape is not None:
            parts.append("\\" + escape)
            continue

        if character == "#" and index + 1 < length and value[index + 1] in "${@":
            parts.append("\\#")
            continue

        if codepoint < 0x20 or codepoint == 0x7F or codepoint in {0x2028, 0x2029}:
            parts.append(f"\\u{codepoint:04X}")
            continue

        parts.append(character)

    parts.append('"')
    return "".join(parts)


def _ruby_inspect(value: object, seen: set[int]) -> str:
    """Recursive implementation of Ruby Liquid's inspect semantics."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _ruby_string_inspect(value)

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in seen:
            return "{...}"
        seen.add(identity)
        try:
            pairs = (
                f"{_ruby_inspect(key, seen)}=>{_ruby_inspect(item, seen)}"
                for key, item in value.items()
            )
            return "{" + ", ".join(pairs) + "}"
        finally:
            seen.remove(identity)

    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in seen:
            return "[...]"
        seen.add(identity)
        try:
            return "[" + ", ".join(_ruby_inspect(item, seen) for item in value) + "]"
        finally:
            seen.remove(identity)

    return str(value)


def ruby_inspect(value: object) -> str:
    """Render JSON-compatible values using Ruby Liquid inspection conventions."""
    return _ruby_inspect(value, set())


def ruby_wrap(value: object, _memo: dict[int, object] | None = None) -> object:
    """Recursively wrap mappings while preserving recursive object graphs."""
    memo = {} if _memo is None else _memo

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in memo:
            return memo[identity]
        wrapped: RubyHash = RubyHash()
        memo[identity] = wrapped
        wrapped.update((key, ruby_wrap(item, memo)) for key, item in value.items())
        return wrapped

    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in memo:
            return memo[identity]
        wrapped_list: list[object] = []
        memo[identity] = wrapped_list
        wrapped_list.extend(ruby_wrap(item, memo) for item in value)
        return wrapped_list

    return value
