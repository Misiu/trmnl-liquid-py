"""TRMNL-compatible template rendering semantics.

Ruby Liquid and python-liquid differ in how runtime node errors are rendered in lax
mode. Ruby Liquid renders most runtime errors into the output stream, while
python-liquid reports them to ``Environment.error()`` and emits no text.

Compatibility references:
- Ruby Liquid 5.13 node error handling:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/block_body.rb
- Ruby Liquid 5.13 context error conversion:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/context.rb
- Ruby Liquid 5.13 error formatting:
  https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/errors.rb
- python-liquid 2.3.1 filtered-expression error conversion:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/builtin/expressions/filtered.py
- python-liquid 2.3.1 node ``blank`` contract:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/ast.py
- python-liquid 2.3.1 BoundTemplate rendering:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/template.py
- python-liquid 2.3.1 documented ``Environment.template_class`` extension point:
  https://github.com/jg-rp/liquid/blob/v2.3.1/liquid/environment.py
"""

from __future__ import annotations

from typing import TextIO

from liquid.exceptions import (
    LiquidError,
    LiquidInterrupt,
    LiquidSyntaxError,
    LiquidTypeError,
    StopRender,
    TemplateNotFoundError,
)
from liquid.template import BoundTemplate


def _ruby_template_not_found_message(error: TemplateNotFoundError) -> str:
    """Format a missing-template error like Ruby Liquid's FileSystemError.

    TRMNL's MemorySystem raises ``Liquid::FileSystemError`` with the message
    ``Template not found: <name>.``. Ruby Liquid prefixes runtime errors with
    ``Liquid error: `` when rendering a node.

    References:
    https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/memory_system.rb
    https://github.com/Shopify/liquid/blob/v5.13.0/lib/liquid/errors.rb
    """
    name = str(error.args[0]) if error.args else ""
    return f"Liquid error: Template not found: {name}."


def _ruby_internal_error_message(error: LiquidError) -> str | None:
    """Map host-language filter errors to Ruby Liquid's generic internal error.

    Ruby Liquid's ``Context#handle_error`` converts non-``Liquid::Error``
    exceptions to ``Liquid::InternalError('internal')``. python-liquid instead
    wraps a Python ``TypeError`` raised by a filter in ``LiquidTypeError`` before
    the template node sees it. The original exception remains available as the
    standard Python exception cause, which lets us reproduce Ruby's behavior
    without changing filter return values or parsing internals.
    """
    if isinstance(error, LiquidTypeError) and isinstance(error.__cause__, TypeError):
        return "Liquid error: internal"
    return None


def _render_liquid_error(error: LiquidError, *, node_blank: bool, buffer: TextIO) -> None:
    """Render the subset of runtime errors whose Ruby form emits node output."""
    message = _ruby_internal_error_message(error)
    if message is not None and not node_blank:
        buffer.write(message)


class TRMNLBoundTemplate(BoundTemplate):
    """BoundTemplate with Ruby Liquid-compatible runtime error output.

    ``Environment.template_class`` is the public python-liquid extension point for
    replacing the bound template implementation. We keep python-liquid's rendering
    algorithm and adapt only evidenced runtime-error output differences required by
    the TRMNL 0.8.2 compatibility surface.
    """

    def render_with_context(
        self,
        context: object,
        buffer: TextIO,
        *args: object,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: object,
    ) -> None:
        """Render using python-liquid's node loop with Ruby runtime-error output."""
        from liquid.context import RenderContext

        if not isinstance(context, RenderContext):
            raise TypeError("context must be a RenderContext")

        namespace = self.make_partial_namespace(partial, dict(*args, **kwargs))
        with context.extend(namespace=namespace):
            for node in self.nodes:
                try:
                    node.render(context, buffer)
                except LiquidInterrupt as error:
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(
                                f"unexpected '{error}'", token=node.token
                            )
                        )
                    else:
                        raise
                except StopRender:
                    break
                except TemplateNotFoundError as error:
                    buffer.write(_ruby_template_not_found_message(error))
                    self.env.error(error, token=node.token)
                except LiquidError as error:
                    _render_liquid_error(error, node_blank=node.blank, buffer=buffer)
                    self.env.error(error, token=node.token)

    async def render_with_context_async(
        self,
        context: object,
        buffer: TextIO,
        *args: object,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: object,
    ) -> None:
        """Async equivalent of :meth:`render_with_context`."""
        from liquid.context import RenderContext

        if not isinstance(context, RenderContext):
            raise TypeError("context must be a RenderContext")

        namespace = self.make_partial_namespace(partial, dict(*args, **kwargs))
        with context.extend(namespace=namespace):
            for node in self.nodes:
                try:
                    await node.render_async(context, buffer)
                except LiquidInterrupt as error:
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(
                                f"unexpected '{error}'", token=node.token
                            )
                        )
                    else:
                        raise
                except StopRender:
                    break
                except TemplateNotFoundError as error:
                    buffer.write(_ruby_template_not_found_message(error))
                    self.env.error(error, token=node.token)
                except LiquidError as error:
                    _render_liquid_error(error, node_blank=node.blank, buffer=buffer)
                    self.env.error(error, token=node.token)
