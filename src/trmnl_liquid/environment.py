"""TRMNL-compatible Python Liquid environment."""

from __future__ import annotations

import re
from typing import Any

from liquid import Environment as LiquidEnvironment
from liquid import Mode
from liquid.loader import BaseLoader

from . import filters
from .memory_system import MemorySystem
from .template_tag import TemplateTag

_QR_COMMA_ARGUMENTS = re.compile(r"(\|\s*qr_code)\s*,")


def _normalize_trmnl_syntax(source: str) -> str:
    """Normalize Ruby Liquid syntax not accepted by python-liquid.

    Ruby Liquid accepts a comma between a filter name and its first argument.
    TRMNL 0.8.2 uses that form in its documented/tested ``qr_code`` surface.
    Python Liquid requires a colon, so normalize only that TRMNL-specific form.
    """
    return _QR_COMMA_ARGUMENTS.sub(r"\1:", source)


class Environment(LiquidEnvironment):
    """Liquid environment configured for TRMNL Liquid 0.8.2 compatibility.

    Defaults intentionally follow Ruby Liquid's non-autoescaped, lax rendering
    model rather than OpenDisplay Studio's previous hardened POC settings.
    """

    def __init__(
        self,
        *,
        file_system: BaseLoader | None = None,
        **kwargs: Any,
    ) -> None:
        loader = kwargs.pop("loader", None)
        if file_system is not None and loader is not None:
            raise TypeError("pass either file_system or loader, not both")

        fallback = file_system or loader
        kwargs["loader"] = (
            fallback
            if isinstance(fallback, MemorySystem)
            else MemorySystem(fallback=fallback)
        )
        kwargs.setdefault("autoescape", False)
        kwargs.setdefault("strict_filters", False)
        kwargs.setdefault("tolerance", Mode.LAX)
        super().__init__(**kwargs)

        self.add_tag(TemplateTag)
        self.add_filter("append_random", filters.append_random)
        self.add_filter("days_ago", filters.days_ago)
        self.add_filter("group_by", filters.group_by)
        self.add_filter("find_by", filters.find_by)
        self.add_filter("markdown_to_html", filters.markdown_to_html)
        self.add_filter("number_with_delimiter", filters.number_with_delimiter)
        self.add_filter("number_to_currency", filters.number_to_currency)
        self.add_filter("l_word", filters.l_word)
        self.add_filter("l_date", filters.l_date)
        self.add_filter("map_to_i", filters.map_to_i)
        self.add_filter("pluralize", filters.pluralize)
        self.add_filter("json", filters.json)
        self.add_filter("parse_json", filters.parse_json)
        self.add_filter("sample", filters.sample)
        self.add_filter("where_exp", filters.where_exp)
        self.add_filter("ordinalize", filters.ordinalize)
        self.add_filter("qr_code", filters.qr_code)

    def from_string(
        self,
        source: str,
        name: str = "",
        path: str | None = None,
        globals: dict[str, object] | None = None,
        matter: dict[str, object] | None = None,
    ):
        """Parse source after applying TRMNL/Ruby Liquid syntax compatibility shims."""
        return super().from_string(
            _normalize_trmnl_syntax(source),
            name=name,
            path=path,
            globals=globals,
            matter=matter,
        )


def render(source: str, /, **data: object) -> str:
    """Render a Liquid template using a fresh TRMNL environment."""
    return Environment().render(source, **data)
