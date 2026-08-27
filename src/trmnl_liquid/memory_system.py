"""In-memory template storage compatible with TRMNL Liquid's MemorySystem."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from liquid.exceptions import TemplateNotFoundError
from liquid.loader import BaseLoader, TemplateSource

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.environment import Environment


class MemorySystem(BaseLoader):
    """Store templates registered by ``{% template %}`` in memory.

    A MemorySystem belongs to one :class:`trmnl_liquid.Environment`, matching the
    lifetime of TRMNL::Liquid::MemorySystem in the Ruby implementation.
    """

    def __init__(
        self,
        templates: Mapping[str, str] | None = None,
        *,
        fallback: BaseLoader | None = None,
    ) -> None:
        self._templates = dict(templates or {})
        self._fallback = fallback

    def register(self, name: str, body: str) -> str:
        """Register *body* under *name* and return the registered body."""
        self._templates[name] = body
        return body

    def read_template_file(self, name: object) -> str:
        """Read a registered template or raise a Liquid template error."""
        key = str(name)
        try:
            return self._templates[key]
        except KeyError as error:
            raise TemplateNotFoundError(
                f"Liquid error: Template not found: {key}.", token=None
            ) from error

    def get_source(
        self,
        env: Environment,
        template_name: str,
        *,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        try:
            body = self._templates[template_name]
        except KeyError:
            if self._fallback is not None:
                try:
                    return self._fallback.get_source(
                        env, template_name, context=context, **kwargs
                    )
                except TemplateNotFoundError:
                    pass

            # Python Liquid's lax mode suppresses TemplateNotFoundError whereas Ruby
            # Liquid renders it. Return an error template to preserve Ruby output.
            body = f"Liquid error: Template not found: {template_name}."

        return TemplateSource(body, template_name, None)
