from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from liquid.exceptions import TemplateNotFoundError

from trmnl_liquid.filters import (
    append_random,
    days_ago,
    markdown_to_html,
    ordinalize,
    ordinalize_number,
    sample,
)
from trmnl_liquid.memory_system import MemorySystem


def test_fallback_ordinalize_examples() -> None:
    """Mirror fallback_spec.rb's direct ordinal helper examples."""
    assert ordinalize_number(0) == "0th"
    assert ordinalize_number(1) == "1st"
    assert ordinalize_number(10) == "10th"
    assert ordinalize_number(100) == "100th"


def test_append_random_contract() -> None:
    """SecureRandom is stubbed upstream; Python verifies the equivalent contract."""
    result = append_random("chart-")
    assert re.fullmatch(r"chart-[0-9a-f]{4}", result)


def test_days_ago_examples() -> None:
    """Mirror upstream's time-dependent default, timezone and formatting examples."""
    utc_today = datetime.now(ZoneInfo("Etc/UTC")).date()
    london_today = datetime.now(ZoneInfo("Europe/London")).date()

    assert days_ago(3) == utc_today - timedelta(days=3)
    assert days_ago(10, "Europe/London") == london_today - timedelta(days=10)
    assert (utc_today - timedelta(days=5)).strftime("%b %d, %Y") == days_ago(5).strftime(
        "%b %d, %Y"
    )


def test_markdown_none_contract() -> None:
    assert markdown_to_html(None) == ""


def test_sample_contract() -> None:
    numbers = ["1", "2", "3", "4", "5"]
    words = ["one", "two", "three"]

    assert sample(numbers) in numbers
    assert sample(words) in words


def test_ordinalize_dynamic_date_contract() -> None:
    now = datetime.now()
    expected = f"{now.strftime('%B')} {ordinalize_number(now.day)}"

    assert ordinalize("now", "%B <<ordinal_day>>") == expected
    assert ordinalize("today", "%B <<ordinal_day>>") == expected


def test_memory_system_examples() -> None:
    system = MemorySystem()

    assert system.register("test", "A body.") == "A body."
    assert system.read_template_file("test") == "A body."

    with pytest.raises(TemplateNotFoundError) as caught:
        system.read_template_file("bogus")
    assert caught.value.args == ("Liquid error: Template not found: bogus.",)
