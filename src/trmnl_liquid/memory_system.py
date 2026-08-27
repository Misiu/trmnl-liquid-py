"""In-memory template storage compatible with TRMNL Liquid's MemorySystem.

Compatibility references:
- TRMNL 0.8.2 MemorySystem:
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/memory_system.rb
- python-liquid 2.3.1 loader contract and ``TemplateNotFoundError``:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/loader.py
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/exceptions.py
"""

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

    Ruby TRMNL reference:
    https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/memory_system.rb

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
        """Read a registered template or raise a Liquid template error.

        Ruby raises ``Liquid::FileSystemError`` when the name is absent. The
        corresponding python-liquid loader exception is ``TemplateNotFoundError``.

        Ruby reference:
        https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/memory_system.rb
        Python reference:
        https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/exceptions.py
        """
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
        """Load a template source or delegate to the configured fallback loader.

        Unlike the previous implementation, this method never fabricates a template
        containing an error message. Missing templates remain loader errors and are
        handled by the rendering layer.

        Python loader reference:
        https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/loader.py
        """
        try:
            body = self._templates[template_name]
        except KeyError as error:
            if self._fallback is not None:
                try:
                    return self._fallback.get_source(
                        env, template_name, context=context, **kwargs
                    )
                except TemplateNotFoundError:
                    pass

            raise TemplateNotFoundError(template_name, token=None) from error

        return TemplateSource(body, template_name, None)
