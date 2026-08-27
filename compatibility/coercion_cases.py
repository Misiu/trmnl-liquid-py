"""Coercion-heavy Ruby/Python differential cases.

These cases intentionally exercise values near Ruby/Python conversion boundaries.
They are kept separate from the broader generated corpus so failures can be
reviewed as compatibility evidence rather than hidden in implementation tests.
"""

from __future__ import annotations

from typing import Any


def coercion_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    map_inputs: list[list[object]] = [
        ["0", "1", "-1"],
        ["001", "-001", "+001"],
        ["  12", "\t-7", " +9"],
        ["12px", "-7.9", "+4foo"],
        ["abc", "", "   "],
        [0, 1, -1],
        [1.9, -1.9, 0.0],
        [None, "0", None],
        [True, False],
        ["9223372036854775808", "-9223372036854775809"],
    ]
    for index, values in enumerate(map_inputs):
        cases.append(
            {
                "name": f"coercion map_to_i {index}",
                "template": "{{ values | map_to_i }}",
                "data": {"values": values},
            }
        )

    plural_cases: list[tuple[object, str, object | None]] = [
        (0, "item", None),
        (1, "item", None),
        (2, "item", None),
        (-1, "item", None),
        (1.0, "item", None),
        ("1", "item", None),
        ("01", "item", None),
        (None, "item", None),
        (2, "person", "people"),
        (0, "mouse", "mice"),
        (True, "item", None),
        (False, "item", None),
    ]
    for index, (count, singular, plural) in enumerate(plural_cases):
        template = "{{ singular | pluralize: count }}"
        data: dict[str, object] = {"singular": singular, "count": count}
        if plural is not None:
            template = "{{ singular | pluralize: count, plural: plural }}"
            data["plural"] = plural
        cases.append(
            {
                "name": f"coercion pluralize {index}",
                "template": template,
                "data": data,
            }
        )

    delimiter_values: list[object] = [
        True,
        False,
        " 1234",
        "+1234",
        "1e3",
        "1_000",
        "1234.",
        ".5",
    ]
    for index, value in enumerate(delimiter_values):
        cases.append(
            {
                "name": f"coercion delimiter {index}",
                "template": "{{ value | number_with_delimiter }}",
                "data": {"value": value},
            }
        )

    currency_cases: list[tuple[object, str, str, str, int]] = [
        (True, "$", ",", ".", 2),
        (False, "$", ",", ".", 2),
        (None, "$", ",", ".", 2),
        ("+1234", "$", ",", ".", 2),
        ("12px", "€", ".", ",", 3),
        (-0.01, "USD ", ",", ".", 4),
        (1234.5, "", " ", ",", 0),
    ]
    for index, (value, unit, delimiter, separator, precision) in enumerate(
        currency_cases
    ):
        cases.append(
            {
                "name": f"coercion currency {index}",
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

    where_cases: list[tuple[list[dict[str, object]], str]] = [
        ([{"value": None}, {"value": 0}, {"value": ""}], "item.value == nil"),
        ([{"value": True}, {"value": False}], "item.value == true"),
        ([{"value": True}, {"value": False}], "item.value == false"),
        ([{"value": 1}, {"value": "1"}], "item.value == 1"),
        ([{"value": 1}, {"value": "1"}], "item.value == '1'"),
        ([{"value": -1}, {"value": 0}, {"value": 1}], "item.value > 0"),
        ([{"value": 1.0}, {"value": 1.5}], "item.value >= 1.5"),
        ([{"name": ""}, {}], "item.name == empty"),
        ([{"name": "abc"}, {"name": "ABC"}], "item.name == 'abc'"),
        ([{"a": True, "b": False}, {"a": True, "b": True}], "item.a and item.b"),
    ]
    for index, (values, expression) in enumerate(where_cases):
        cases.append(
            {
                "name": f"coercion where_exp {index}",
                "template": "{{ values | where_exp: 'item', expression }}",
                "data": {"values": values, "expression": expression},
            }
        )

    json_cases: list[tuple[str, object]] = [
        ("scalar string", '"001"'),
        ("scalar null", "null"),
        ("scalar boolean", "true"),
        ("nested mixed", '{"a":[0,false,null,"1"],"b":{"c":-1.5}}'),
        ("unicode escapes", '{"text":"\\u0141\\u00f3d\\u017a"}'),
    ]
    for name, encoded in json_cases:
        cases.append(
            {
                "name": f"coercion parse_json {name}",
                "template": "{{ value | parse_json }}",
                "data": {"value": encoded},
            }
        )

    assert len(cases) == 52
    return cases
