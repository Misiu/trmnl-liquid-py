from __future__ import annotations

from trmnl_liquid import Environment


def render(template: str, **data: object) -> str:
    return Environment().render(template, **data)


def test_ruby_lax_filter_argument_separator_in_output() -> None:
    assert render('{{ "a" | append, "b" }}') == "ab"


def test_standard_colon_filter_argument_separator_still_works() -> None:
    assert render('{{ "a" | append: "b" }}') == "ab"


def test_ruby_lax_filter_separator_applies_to_chained_filters() -> None:
    assert render('{{ "a" | append, "b" | append, "c" }}') == "abc"


def test_filter_argument_commas_are_not_reclassified() -> None:
    assert render('{{ "a" | append: ",b" }}') == "a,b"


def test_ruby_lax_filter_argument_separator_in_assign() -> None:
    template = '{% assign value = "a" | append, "b" %}{{ value }}'
    assert render(template) == "ab"


def test_ruby_lax_filter_argument_separator_in_echo() -> None:
    assert render('{% echo "a" | append, "b" %}') == "ab"


def test_trmnl_qr_comma_syntax_matches_colon_syntax() -> None:
    ruby_lax = render('{{ "Test" | qr_code, 11, "", "fixed" }}')
    standard = render('{{ "Test" | qr_code: 11, "", "fixed" }}')
    assert ruby_lax == standard


def test_ruby_lax_adapter_does_not_rewrite_template_source_text() -> None:
    assert render("literal | qr_code, 11") == "literal | qr_code, 11"
