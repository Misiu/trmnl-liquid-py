"""Ruby-style value wrappers used for output compatibility."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


class RubyHash(dict[Any, Any]):
    """A dict whose string representation matches Ruby Hash#inspect."""

    def __str__(self) -> str:
        return ruby_inspect(self)

    def __repr__(self) -> str:
        return ruby_inspect(self)


def ruby_inspect(value: object) -> str:
    """Render JSON-compatible values using Ruby's inspect conventions."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, Mapping):
        pairs = (f"{ruby_inspect(key)}=>{ruby_inspect(item)}" for key, item in value.items())
        return "{" + ", ".join(pairs) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(ruby_inspect(item) for item in value) + "]"
    return str(value)


def ruby_wrap(value: object) -> object:
    """Recursively wrap mappings so Liquid output looks like Ruby Liquid output."""
    if isinstance(value, Mapping):
        return RubyHash((key, ruby_wrap(item)) for key, item in value.items())
    if isinstance(value, list):
        return [ruby_wrap(item) for item in value]
    if isinstance(value, tuple):
        return [ruby_wrap(item) for item in value]
    return value
