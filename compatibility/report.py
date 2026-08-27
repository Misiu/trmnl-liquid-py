"""Generate and validate the README compatibility evidence block.

The report uses the same checked-in fixed, generated, coercion, date/time,
template/error, and upstream-spec corpora as the Ruby/Python compatibility gate.
``compare.py`` proves output equality; this module keeps documented counts
synchronized with those sources.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from compatibility.coercion_cases import coercion_cases
from compatibility.date_time_cases import date_time_cases
from compatibility.generated_cases import generated_cases
from compatibility.template_error_cases import template_error_cases
from compatibility.upstream_cases import upstream_differential_cases
from compatibility.upstream_specs import UPSTREAM_SPEC_EXAMPLES

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "compatibility" / "cases.json"
README = ROOT / "README.md"
REPORT_START = "<!-- compatibility-report:start -->"
REPORT_END = "<!-- compatibility-report:end -->"


@dataclass(frozen=True)
class CompatibilityMetrics:
    """Counts derived from the compatibility corpus and upstream spec manifest."""

    fixed_cases: int
    generated_cases: int
    upstream_differential_cases: int
    differential_cases: int
    upstream_examples: int
    upstream_property_examples: int
    upstream_deferred_examples: int


def collect_metrics() -> CompatibilityMetrics:
    """Collect report metrics from the same checked-in sources used by CI."""
    fixed = json.loads(CASES.read_text(encoding="utf-8"))
    if not isinstance(fixed, list):
        raise ValueError("compatibility/cases.json must contain a JSON array")

    generated_count = (
        len(generated_cases())
        + len(coercion_cases())
        + len(date_time_cases())
        + len(template_error_cases())
    )
    upstream_cases_count = len(upstream_differential_cases())
    statuses = Counter(example.status for example in UPSTREAM_SPEC_EXAMPLES)

    if statuses["differential"] != upstream_cases_count:
        raise ValueError(
            "upstream differential manifest count does not match upstream case corpus"
        )

    return CompatibilityMetrics(
        fixed_cases=len(fixed),
        generated_cases=generated_count,
        upstream_differential_cases=upstream_cases_count,
        differential_cases=len(fixed) + generated_count + upstream_cases_count,
        upstream_examples=len(UPSTREAM_SPEC_EXAMPLES),
        upstream_property_examples=statuses["property"],
        upstream_deferred_examples=statuses["deferred"],
    )


def render_report(metrics: CompatibilityMetrics | None = None) -> str:
    """Render the generated README compatibility block."""
    current = metrics or collect_metrics()
    supported_upstream = (
        current.upstream_differential_cases + current.upstream_property_examples
    )

    lines = [
        REPORT_START,
        "### Compatibility evidence",
        "",
        "| Gate | Result |",
        "| --- | ---: |",
        (
            "| Ruby 0.8.2 vs Python exact differential corpus | "
            f"**{current.differential_cases}/{current.differential_cases}** |"
        ),
        "| Known mismatches in the supported scope | **0** |",
        (
            "| Official TRMNL 0.8.2 RSpec examples mapped | "
            f"**{current.upstream_examples}/{current.upstream_examples}** |"
        ),
        (
            "| Upstream examples covered by exact differential tests | "
            f"**{current.upstream_differential_cases}** |"
        ),
        (
            "| Upstream examples covered by property/unit tests | "
            f"**{current.upstream_property_examples}** |"
        ),
        (
            "| Upstream examples covered in the initial non-I18n scope | "
            f"**{supported_upstream}/{current.upstream_examples}** |"
        ),
        (
            "| Deferred Rails/I18n upstream examples | "
            f"**{current.upstream_deferred_examples}** |"
        ),
        "| Python CI matrix | **3.11, 3.12, 3.13, 3.14** |",
        "| Comparison | **exact rendered output** |",
        "",
        (
            "The `Compatibility` workflow runs the Ruby oracle first and fails on any "
            "mismatch. It then checks that this generated report still matches the "
            "checked-in corpus and upstream-spec manifest."
        ),
        REPORT_END,
    ]
    return "\n".join(lines)


def updated_readme(source: str, report: str | None = None) -> str:
    """Replace the generated README block while preserving surrounding text."""
    if REPORT_START not in source or REPORT_END not in source:
        raise ValueError("README compatibility report markers are missing")

    before, remainder = source.split(REPORT_START, maxsplit=1)
    _, after = remainder.split(REPORT_END, maxsplit=1)
    block = report or render_report()
    return f"{before.rstrip()}\n\n{block}\n\n{after.lstrip()}"


def check_readme() -> bool:
    """Return whether README contains the current generated compatibility report."""
    source = README.read_text(encoding="utf-8")
    return source == updated_readme(source)


def write_readme() -> None:
    """Update README with the current generated compatibility report."""
    source = README.read_text(encoding="utf-8")
    README.write_text(updated_readme(source), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.write:
        write_readme()
        return 0
    if args.check:
        if check_readme():
            return 0
        print("README compatibility report is stale; run python -m compatibility.report --write")
        return 1

    print(render_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
