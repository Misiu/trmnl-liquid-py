"""Deterministic date/time Ruby/Python differential cases.

``days_ago`` intentionally is not included here because upstream computes from
``TZInfo::Timezone#get(...).now``. Putting wall-clock-dependent expectations in
the permanent exact-output corpus would make the compatibility gate flaky around
local midnight. Its timezone/boundary semantics are covered by frozen-clock unit
and property tests instead.
"""

from __future__ import annotations

from typing import Any


def date_time_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    values_and_formats: list[tuple[object, str]] = [
        ("2024-02-29", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-01", "%A, %B <<ordinal_day>>, %Y"),
        ("2025-01-02", "%A %b <<ordinal_day>>"),
        ("2025-01-03", "%Y/<<ordinal_day>>/%m"),
        ("2025-01-04", "<<ordinal_day>> %B %Y"),
        ("2025-01-10", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-11", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-12", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-13", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-20", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-21", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-22", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-23", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-24", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-30", "%Y-%m-<<ordinal_day>>"),
        ("2025-01-31", "%Y-%m-<<ordinal_day>>"),
        ("2000-02-29 23:59:59 +0000", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2038-01-19 03:14:07 +0000", "%A %B <<ordinal_day>> %Y %H:%M:%S"),
        ("2025-03-30 01:59:59 +0100", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2025-03-30 03:00:00 +0200", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2025-10-26 02:30:00 +0200", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2025-10-26 02:30:00 +0100", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2025-12-31 23:59:59 +1400", "%A, %B <<ordinal_day>>, %Y %z"),
        ("2025-01-01 00:00:00 -1200", "%A, %B <<ordinal_day>>, %Y %z"),
        ("2025-07-14 12:34:56 +0530", "%Y-%m-<<ordinal_day>> %H:%M:%S %z"),
        ("2025-07-14T12:34:56Z", "%Y %b <<ordinal_day>> %H:%M:%S %z"),
        (0, "%Y-%m-<<ordinal_day>> %H:%M:%S"),
        (1, "%Y-%m-<<ordinal_day>> %H:%M:%S"),
        (1770134949, "%A, %B <<ordinal_day>>, %Y %H:%M:%S"),
        (2147483647, "%Y-%m-<<ordinal_day>> %H:%M:%S"),
    ]

    for index, (value, format_string) in enumerate(values_and_formats):
        cases.append(
            {
                "name": f"date time ordinalize {index}",
                "template": "{{ value | ordinalize: format }}",
                "data": {"value": value, "format": format_string},
            }
        )

    assert len(cases) == 30
    return cases
