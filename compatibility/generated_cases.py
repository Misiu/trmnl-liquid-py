"""Deterministic generated cases for Ruby/Python differential compatibility tests."""

from __future__ import annotations

from typing import Any


def generated_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    numbers: list[object] = [
        0,
        1,
        -1,
        12,
        999,
        1000,
        1001,
        1234567,
        -1234567,
        0.1,
        12.34,
        -9876.543,
        "000123",
        "-000123.40",
        "12px",
        "",
        None,
    ]
    separator_sets = [(",", "."), (".", ","), (" ", ","), ("_", ":")]
    for index, number in enumerate(numbers):
        for delimiter, separator in separator_sets:
            cases.append(
                {
                    "name": f"generated delimiter {index} {delimiter!r} {separator!r}",
                    "template": "{{ value | number_with_delimiter: delimiter, separator }}",
                    "data": {
                        "value": number,
                        "delimiter": delimiter,
                        "separator": separator,
                    },
                }
            )

    currency_values: list[object] = [0, 1, -1, 12.3, 1234.5678, "00012.30", "abc"]
    currency_formats = [
        ("$", ",", ".", 0),
        ("$", ",", ".", 2),
        ("€", ".", ",", 3),
        ("PLN ", " ", ",", 1),
        ("", "_", ":", 4),
    ]
    for value_index, value in enumerate(currency_values):
        for format_index, (unit, delimiter, separator, precision) in enumerate(
            currency_formats
        ):
            cases.append(
                {
                    "name": f"generated currency {value_index} {format_index}",
                    "template": (
                        "{{ value | number_to_currency: unit, delimiter, separator, precision }}"
                    ),
                    "data": {
                        "value": value,
                        "unit": unit,
                        "delimiter": delimiter,
                        "separator": separator,
                        "precision": precision,
                    },
                }
            )

    markdown_inputs = [
        "plain text",
        "**bold** and *emphasis*",
        "`inline code`",
        "> quote",
        "## Heading 2\n\nParagraph",
        "### Heading 3\n\n- one\n- two",
        "1. one\n2. two\n3. three",
        "[OpenAI](https://openai.com)",
        "<https://example.com>",
        "---",
        "line one\n\nline two",
        "special < > & \" ' characters",
        "Unicode: Łódź, 日本語, 😀",
        "    indented code\n    second line",
        "Paragraph\n\n> quote\n\nParagraph",
    ]
    for index, markdown in enumerate(markdown_inputs):
        cases.append(
            {
                "name": f"generated markdown {index}",
                "template": "{{ value | markdown_to_html }}",
                "data": {"value": markdown},
            }
        )

    collections = [
        [],
        [{"id": 1, "active": True}, {"id": 2, "active": False}],
        [{"id": 1, "score": 9}, {"id": 2, "score": 10}, {"id": 3, "score": 11}],
        [{"name": "a"}, {"name": "b"}, {"other": "missing"}],
    ]
    expressions = [
        "item.id == 1",
        "item.id != 1",
        "item.id > 1",
        "item.id >= 2",
        "item.id < 3",
        "item.active == true",
        "item.name == 'a' or item.name == 'b'",
        "item.score >= 10 and item.id > 1",
        "item.missing == nil",
    ]
    for collection_index, collection in enumerate(collections):
        for expression_index, expression in enumerate(expressions):
            cases.append(
                {
                    "name": f"generated where_exp {collection_index} {expression_index}",
                    "template": "{{ values | where_exp: 'item', expression }}",
                    "data": {"values": collection, "expression": expression},
                }
            )

    qr_values = [
        "Test",
        "Hello world",
        "https://example.com/path?q=1",
        "Łódź",
        "日本語",
        "😀 QR",
        "123456789012345678901234567890",
    ]
    qr_levels = ["l", "m", "q", "h", "invalid"]
    qr_options = [(1, "responsive"), (4, "responsive"), (11, "responsive"), (3, "fixed")]
    for value_index, value in enumerate(qr_values):
        for level in qr_levels:
            for size, view in qr_options:
                cases.append(
                    {
                        "name": f"generated qr {value_index} {level} {size} {view}",
                        "template": "{{ value | qr_code: size, level, view }}",
                        "data": {"value": value, "size": size, "level": level, "view": view},
                    }
                )

    ordinal_dates = [
        "2025-01-01",
        "2025-01-02",
        "2025-01-03",
        "2025-01-04",
        "2025-01-11",
        "2025-01-12",
        "2025-01-13",
        "2025-01-21",
        "2025-01-22",
        "2025-01-23",
        "2025-01-31",
    ]
    for index, value in enumerate(ordinal_dates):
        cases.append(
            {
                "name": f"generated ordinalize {index}",
                "template": "{{ value | ordinalize: '%Y-%m-<<ordinal_day>>' }}",
                "data": {"value": value},
            }
        )

    template_names = ["a", "A1", "hello_world", "folder/item", "a/b_c/123"]
    for index, name in enumerate(template_names):
        cases.append(
            {
                "name": f"generated template valid name {index}",
                "template": (
                    f"{{% template {name} %}}  before {{{{ value }}}} after  "
                    f"{{% endtemplate %}}{{% render '{name}', value: 'X' %}}"
                ),
                "data": {},
            }
        )

    invalid_names = ["bad-name", "bad.name", "bad!", "hello world", "@"]
    for index, name in enumerate(invalid_names):
        cases.append(
            {
                "name": f"generated template invalid name {index}",
                "template": f"{{% template {name} %}}body{{% endtemplate %}}",
                "data": {},
            }
        )

    json_values: list[object] = [
        None,
        True,
        False,
        0,
        -1,
        "text",
        "Łódź",
        [1, "a", None, True],
        {"a": 1, "nested": {"b": [2, 3]}},
    ]
    for index, value in enumerate(json_values):
        cases.append(
            {
                "name": f"generated json {index}",
                "template": "{{ value | json }}",
                "data": {"value": value},
            }
        )

    return cases
