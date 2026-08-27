"""Ruby scalar coercion helpers used by TRMNL fallback filters.

TRMNL 0.8.2 delegates several fallback operations directly to Ruby ``to_s`` and
``to_i`` semantics. Python differs materially for ``None`` and booleans, so these
conversions live in one explicit compatibility module rather than being repeated
inside individual filters.

References:
- TRMNL 0.8.2 filters:
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/filters.rb
- TRMNL 0.8.2 fallback helpers:
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/fallback.rb
- Ruby 4.0.6 NilClass#to_i:
  https://github.com/ruby/ruby/blob/03b6d3f889/nilclass.rb
- Ruby 4.0.6 NilClass/TrueClass/FalseClass#to_s:
  https://github.com/ruby/ruby/blob/03b6d3f889/object.c
"""

from __future__ import annotations

import re

_TO_I = re.compile(r"^[\s]*([+-]?\d+)")


def ruby_to_s(value: object) -> str:
    """Convert JSON-compatible scalar values like Ruby ``Object#to_s`` variants."""
    if value is None:
        return ""
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def ruby_to_i(value: object) -> int:
    """Match Ruby 4.0.6 ``to_i`` for scalar values used by TRMNL filters."""
    if value is None:
        # Ruby 4.0 added NilClass#to_i returning zero.
        return 0
    if isinstance(value, bool):
        # TrueClass/FalseClass do not implement #to_i. Raising here lets Liquid
        # render the same generic runtime error as the Ruby implementation.
        raise TypeError("Ruby booleans do not implement to_i")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        match = _TO_I.match(value)
        return int(match.group(1)) if match else 0
    raise TypeError(f"Ruby {type(value).__name__} values do not implement to_i")
