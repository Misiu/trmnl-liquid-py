from __future__ import annotations

from datetime import datetime as RealDateTime
from datetime import tzinfo

import pytest

from trmnl_liquid import filters


class _FrozenDateTime(RealDateTime):
    frozen_now: RealDateTime

    @classmethod
    def now(cls, tz: tzinfo | None = None) -> RealDateTime:
        if tz is None:
            return cls.frozen_now.replace(tzinfo=None)
        return cls.frozen_now.astimezone(tz)


@pytest.mark.parametrize(
    ("instant", "timezone", "days", "expected"),
    [
        # Same UTC instant is already the next local day in Warsaw.
        (RealDateTime.fromisoformat("2025-03-29T23:30:00+00:00"), "Europe/Warsaw", 0, "2025-03-30"),
        # Warsaw DST starts on 2025-03-30; local calendar arithmetic must remain date-based.
        (RealDateTime.fromisoformat("2025-03-30T01:30:00+00:00"), "Europe/Warsaw", 1, "2025-03-29"),
        # Warsaw DST ends on 2025-10-26; both repeated-hour instants have the same local date.
        (RealDateTime.fromisoformat("2025-10-26T00:30:00+00:00"), "Europe/Warsaw", 1, "2025-10-25"),
        (RealDateTime.fromisoformat("2025-10-26T01:30:00+00:00"), "Europe/Warsaw", 1, "2025-10-25"),
        # New York is still on the previous local day for this UTC instant.
        (RealDateTime.fromisoformat("2025-03-09T04:30:00+00:00"), "America/New_York", 0, "2025-03-08"),
        # New York DST transition does not change the date subtraction semantics.
        (RealDateTime.fromisoformat("2025-03-09T07:30:00+00:00"), "America/New_York", 2, "2025-03-07"),
    ],
)
def test_days_ago_uses_local_timezone_date(
    monkeypatch: pytest.MonkeyPatch,
    instant: RealDateTime,
    timezone: str,
    days: int,
    expected: str,
) -> None:
    """Match upstream TZInfo::Timezone#get(...).now.to_date calendar semantics."""
    _FrozenDateTime.frozen_now = instant
    monkeypatch.setattr(filters, "datetime", _FrozenDateTime)

    assert filters.days_ago(days, timezone).isoformat() == expected


def test_days_ago_uses_ruby_integer_coercion(monkeypatch: pytest.MonkeyPatch) -> None:
    _FrozenDateTime.frozen_now = RealDateTime.fromisoformat("2025-08-27T12:00:00+00:00")
    monkeypatch.setattr(filters, "datetime", _FrozenDateTime)

    assert filters.days_ago("  +2days", "Etc/UTC").isoformat() == "2025-08-25"
    assert filters.days_ago(None, "Etc/UTC").isoformat() == "2025-08-27"
