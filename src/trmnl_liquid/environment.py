"""TRMNL-compatible Python Liquid environment."""

from __future__ import annotations

from typing import Any

from liquid import Environment as LiquidEnvironment
from liquid import Mode
from liquid.loader import BaseLoader

from . import filters
from .control_flow import TRMNLForTag, TRMNLIfTag
from .liquid_syntax import RubyLaxAssignTag, RubyLaxEchoTag, RubyLaxOutput
from .memory_system import MemorySystem
from .template import TRMNLBoundTemplate
from .template_tag import TemplateTag


class Environment(LiquidEnvironment):
    """Liquid environment configured for TRMNL Liquid 0.8.2 compatibility.

    Defaults intentionally follow Ruby Liquid's non-autoescaped, lax rendering
    model rather than OpenDisplay Studio's previous hardened POC settings.

    python-liquid exposes ``template_class`` and ``add_tag`` as supported extension
    points. TRMNL uses them to reproduce Ruby Liquid's runtime-error and parsing
    semantics without monkeypatching library internals.

    Python reference:
    https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/environment.py
    """

    template_class = TRMNLBoundTemplate

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

        # python-liquid registers tags by name, so add_tag() is the public extension
        # point for replacing built-in parsers/nodes while preserving the environment.
        #
        # Python references:
        # https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/environment.py
        # https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/__init__.py
        self.add_tag(RubyLaxOutput)
        self.add_tag(RubyLaxAssignTag)
        self.add_tag(RubyLaxEchoTag)
        self.add_tag(TRMNLIfTag)
        self.add_tag(TRMNLForTag)
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


def render(source: str, /, **data: object) -> str:
    """Render a Liquid template using a fresh TRMNL environment."""
    return Environment().render(source, **data)
