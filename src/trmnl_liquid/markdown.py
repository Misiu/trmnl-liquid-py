"""Redcarpet-compatible Markdown rendering for the TRMNL filter surface.

TRMNL 0.8.2 constructs Redcarpet with its default parser extensions and default
HTML renderer options:
https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/filters.rb

Redcarpet references:
https://github.com/vmg/redcarpet/blob/v3.6.1/README.markdown
https://github.com/vmg/redcarpet/blob/v3.6.1/ext/redcarpet/html.c

Mistune 3.3.4 public parser/renderer extension points and token model:
https://github.com/lepture/mistune/blob/v3.3.4/docs/advanced.rst
https://github.com/lepture/mistune/blob/v3.3.4/src/mistune/markdown.py
https://github.com/lepture/mistune/blob/v3.3.4/src/mistune/block_parser.py
https://github.com/lepture/mistune/blob/v3.3.4/src/mistune/inline_parser.py
https://github.com/lepture/mistune/blob/v3.3.4/src/mistune/renderers/html.py
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable
from re import Match
from typing import Any, ClassVar

import mistune

_MARKDOWN_BLOCK_TYPES = frozenset(
    {
        "block_code",
        "block_error",
        "block_html",
        "block_quote",
        "footnote_def",
        "footnotes",
        "heading",
        "list",
        "paragraph",
        "table",
        "thematic_break",
    }
)
_ENTITY = re.compile(
    r"&(?:#[0-9]{1,7};|#[xX][0-9A-Fa-f]+;|[^\t\n\f <&#;]{1,32};)"
)
_MULTILINE_CODESPAN = re.compile(r"(.*?[^`])", re.S)
_LIST_INDENTED_PARAGRAPH = (
    r"^(?: {4}(?! )[^\n]*(?:\n|$))(?: {4}(?! )[^\n]*(?:\n|$))*"
)


def _escape_text_preserving_entities(text: str) -> str:
    """Match Redcarpet's split handling of normal text and entity tokens."""
    parts: list[str] = []
    cursor = 0
    for match in _ENTITY.finditer(text):
        parts.append(
            html.escape(text[cursor : match.start()], quote=True).replace(
                "&#x27;", "&#39;"
            )
        )
        parts.append(match.group(0))
        cursor = match.end()
    parts.append(
        html.escape(text[cursor:], quote=True).replace("&#x27;", "&#39;")
    )
    return "".join(parts)


def _parse_intra_word_emphasis(
    inline: mistune.InlineParser,
    match: Match[str],
    state: mistune.InlineState,
) -> int:
    marker = match.group("redcarpet_intra_marker")
    text = match.group("redcarpet_intra_text")
    token_type = "strong" if len(marker) == 2 else "emphasis"
    state.append_token(
        {
            "type": token_type,
            "children": inline(text, state.env),
        }
    )
    return match.end()


def _parse_redcarpet_codespan(
    inline: mistune.InlineParser,
    match: Match[str],
    state: mistune.InlineState,
) -> int | None:
    """Preserve newlines in multi-line code spans as Redcarpet does."""
    marker = match.group(0)
    pattern = re.compile(
        _MULTILINE_CODESPAN.pattern + re.escape(marker) + r"(?!`)",
        re.S,
    )
    closing = pattern.match(state.src, match.end())
    if closing is None or "\n" not in closing.group(1):
        return inline.parse_codespan(match, state)

    state.append_token({"type": "codespan", "raw": closing.group(1)})
    return closing.end()


class _RedcarpetInlineParser(mistune.InlineParser):
    """Adapt Mistune inline grammar to Redcarpet's default extension set."""

    # Redcarpet treats two trailing spaces as a hard break, but a backslash before
    # a newline remains literal with the default extension set. Mistune's default
    # linebreak rule treats both forms as hard breaks.
    SPECIFICATION: ClassVar[dict[str, str]] = {
        **mistune.InlineParser.SPECIFICATION,
        "linebreak": r"(?: {2,})\n\s*",
    }

    def __init__(self) -> None:
        super().__init__(hard_wrap=False)

        # Redcarpet's `no_intra_emphasis` extension is disabled by default, while
        # Mistune follows CommonMark and suppresses underscores inside words.
        self.register(
            "redcarpet_intra_emphasis",
            (
                r"(?<=\w)(?P<redcarpet_intra_marker>_{1,2})"
                r"(?P<redcarpet_intra_text>[^_\n]+?)"
                r"(?P=redcarpet_intra_marker)(?=\w)"
            ),
            _parse_intra_word_emphasis,
            before="emphasis",
        )

        # Fenced code blocks are not enabled by TRMNL's Redcarpet constructor.
        # Backtick fences therefore fall through to Redcarpet's code-span parser,
        # which preserves embedded newlines unlike Mistune's CommonMark codespan.
        self.register(
            "redcarpet_codespan",
            r"`{1,}",
            _parse_redcarpet_codespan,
            before="codespan",
        )


class _RedcarpetBlockParser(mistune.BlockParser):
    """Use Redcarpet's default block grammar instead of Mistune CommonMark extras."""

    # `fenced_code_blocks` is an opt-in Redcarpet extension and TRMNL passes an
    # empty extension hash. Mistune enables fenced code in its default block rules.
    DEFAULT_RULES = tuple(
        rule for rule in mistune.BlockParser.DEFAULT_RULES if rule != "fenced_code"
    )
    SPECIFICATION: ClassVar[dict[str, str]] = {
        **mistune.BlockParser.SPECIFICATION,
        "redcarpet_list_indented_paragraph": _LIST_INDENTED_PARAGRAPH,
    }

    def __init__(self) -> None:
        list_rules: list[str] = []
        for rule in self.DEFAULT_RULES:
            if rule == "indent_code":
                list_rules.append("redcarpet_list_indented_paragraph")
            list_rules.append(rule)
        super().__init__(list_rules=list_rules)

    def parse_redcarpet_list_indented_paragraph(
        self,
        match: Match[str],
        state: mistune.BlockState,
    ) -> int:
        """Keep Redcarpet's paragraph continuation semantics inside list items."""
        lines = match.group(0).splitlines(keepends=True)
        text = "".join(line[2:] if line.startswith("  ") else line for line in lines)
        state.add_paragraph(text)
        return match.end()


class _RedcarpetRenderer(mistune.HTMLRenderer):
    """Serialize Mistune tokens exactly like Redcarpet::Render::HTML by default."""

    def __init__(self) -> None:
        # Redcarpet allows raw input HTML unless filter_html/escape_html is enabled.
        super().__init__(escape=False)

    def text(self, text: str) -> str:
        return _escape_text_preserving_entities(text)

    def render_tokens(
        self,
        tokens: Iterable[dict[str, Any]],
        state: mistune.BlockState,
    ) -> str:
        # Redcarpet block render callbacks prepend one newline when output already
        # exists. Mistune renderers normally concatenate adjacent blocks directly.
        parts: list[str] = []
        has_output = False
        for token in tokens:
            rendered = self.render_token(token, state)
            if not rendered:
                continue
            if has_output and token.get("type") in _MARKDOWN_BLOCK_TYPES:
                parts.append("\n")
            parts.append(rendered)
            has_output = True
        return "".join(parts)

    def thematic_break(self) -> str:
        return "<hr>\n"

    def linebreak(self) -> str:
        return "<br>\n"

    def codespan(self, text: str) -> str:
        escaped = html.escape(text, quote=True).replace("&#x27;", "&#39;")
        return f"<code>{escaped}</code>"

    def block_code(self, code: str, info: str | None = None) -> str:
        if code and not code.endswith("\n"):
            code += "\n"
        return super().block_code(code, info)

    def block_html(self, raw_html: str) -> str:
        return raw_html if raw_html.endswith("\n") else f"{raw_html}\n"

    def image(self, text: str, url: str, title: str | None = None) -> str:
        rendered = super().image(text, url, title)
        if rendered.endswith(" />"):
            return f"{rendered[:-3]}>"
        return rendered

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        tag = "ol" if ordered else "ul"
        depth = attrs.get("depth", 0)
        prefix = "\n" if isinstance(depth, int) and depth > 0 else ""
        return f"{prefix}<{tag}>\n{text}</{tag}>\n"

    def list_item(self, text: str) -> str:
        return f"<li>{text.rstrip(chr(10))}</li>\n"


class _RedcarpetMarkdown(mistune.Markdown):
    """Preserve Redcarpet paragraph-edge whitespace before inline parsing."""

    def render_state(
        self,
        state: mistune.BlockState,
    ) -> str | list[dict[str, Any]]:
        tokens = self._prepare_tokens(state.tokens, state)
        if self.renderer is not None:
            return self.renderer(tokens, state)
        return tokens

    def _prepare_tokens(
        self,
        tokens: Iterable[dict[str, Any]],
        state: mistune.BlockState,
    ) -> list[dict[str, Any]]:
        prepared: list[dict[str, Any]] = []
        for source_token in tokens:
            token = source_token.copy()
            children = token.get("children")
            if isinstance(children, list):
                token["children"] = self._prepare_tokens(children, state)
            elif "text" in token:
                text = str(token.pop("text"))
                if token.get("type") == "paragraph":
                    # Redcarpet's paragraph renderer skips leading whitespace but
                    # does not trim spaces before the paragraph's structural newline.
                    text = text.lstrip(" \r\n\t\f\v").rstrip("\r\n\t\f\v")
                else:
                    text = text.strip(" \r\n\t\f")
                token["children"] = self.inline(text, state.env)
            prepared.append(token)
        return prepared


_MARKDOWN = _RedcarpetMarkdown(
    renderer=_RedcarpetRenderer(),
    block=_RedcarpetBlockParser(),
    inline=_RedcarpetInlineParser(),
)


def markdown_to_html(markdown: object) -> str:
    """Render Markdown using TRMNL 0.8.2 / Redcarpet 3.6.1 semantics."""
    value = "" if markdown is None else str(markdown)
    return str(_MARKDOWN(value))
