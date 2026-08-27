from __future__ import annotations

from trmnl_liquid.ruby_values import ruby_inspect, ruby_wrap


def test_ruby_string_inspect_uses_ruby_control_escapes() -> None:
    value = "\x00\x07\x08\t\n\x0b\x0c\r\x1b\x1f\x7f"
    assert ruby_inspect(value) == (
        '"\\u0000\\a\\b\\t\\n\\v\\f\\r\\e\\u001F\\u007F"'
    )


def test_ruby_string_inspect_escapes_unicode_line_separators() -> None:
    assert ruby_inspect("before\u2028middle\u2029after") == (
        '"before\\u2028middle\\u2029after"'
    )


def test_ruby_string_inspect_escapes_interpolation_markers() -> None:
    assert ruby_inspect('#{value} #@name #$global #plain') == (
        '"\\#{value} \\#@name \\#$global #plain"'
    )


def test_ruby_string_inspect_preserves_unicode_and_escapes_quotes() -> None:
    assert ruby_inspect('Łódź "test" \\ 日本語') == (
        '"Łódź \\"test\\" \\\\ 日本語"'
    )


def test_ruby_inspect_handles_recursive_hashes() -> None:
    value: dict[str, object] = {}
    value["self"] = value
    assert ruby_inspect(value) == '{"self"=>{...}}'


def test_ruby_inspect_handles_recursive_arrays() -> None:
    value: list[object] = []
    value.append(value)
    assert ruby_inspect(value) == "[[...]]"


def test_ruby_wrap_preserves_recursive_graphs() -> None:
    value: dict[str, object] = {}
    value["self"] = value

    wrapped = ruby_wrap(value)

    assert str(wrapped) == '{"self"=>{...}}'
