"""TRMNL-compatible Python Liquid environment."""

from __future__ import annotations

from typing import Any

from liquid import Environment as LiquidEnvironment
from liquid import Mode

from . import filters


class Environment(LiquidEnvironment):
    """Liquid environment configured with TRMNL 0.8.2 filters.

    Defaults intentionally follow Ruby Liquid's non-autoescaped, lax rendering
    model rather than OpenDisplay Studio's previous hardened POC settings.
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("autoescape", False)
        kwargs.setdefault("strict_filters", False)
        kwargs.setdefault("tolerance", Mode.LAX)
        super().__init__(**kwargs)
        self.add_filter("append_random", filters.append_random)
        self.add_filter("days_ago", filters.days_ago)
        self.add_filter("group_by", filters.group_by)
        self.add_filter("find_by", filters.find_by)
        self.add_filter("number_with_delimiter", filters.number_with_delimiter)
        self.add_filter("number_to_currency", filters.number_to_currency)
        self.add_filter("l_word", filters.l_word)
        self.add_filter("l_date", filters.l_date)
        self.add_filter("map_to_i", filters.map_to_i)
        self.add_filter("pluralize", filters.pluralize)
        self.add_filter("json", filters.json)
        self.add_filter("parse_json", filters.parse_json)
        self.add_filter("sample", filters.sample)


def render(source: str, /, **data: object) -> str:
    """Render a Liquid template using a fresh TRMNL environment."""
    return Environment().render(source, **data)
