from __future__ import annotations

from collections import Counter
from pathlib import Path

from compatibility.upstream_cases import upstream_differential_cases
from compatibility.upstream_specs import UPSTREAM_SPEC_EXAMPLES

ROOT = Path(__file__).resolve().parents[1]


def test_upstream_manifest_counts_all_official_examples() -> None:
    counts = Counter(example.status for example in UPSTREAM_SPEC_EXAMPLES)

    assert len(UPSTREAM_SPEC_EXAMPLES) == 73
    assert counts == {
        "differential": 46,
        "property": 16,
        "deferred": 11,
    }


def test_every_differential_manifest_entry_has_an_exact_oracle_case() -> None:
    case_names = [str(case["name"]) for case in upstream_differential_cases()]
    evidence = [
        example.evidence
        for example in UPSTREAM_SPEC_EXAMPLES
        if example.status == "differential"
    ]

    assert len(case_names) == len(set(case_names)) == 46
    assert len(evidence) == len(set(evidence)) == 46
    assert set(evidence) == set(case_names)


def test_every_property_manifest_entry_points_to_an_existing_test() -> None:
    for example in UPSTREAM_SPEC_EXAMPLES:
        if example.status != "property":
            continue

        relative_path, separator, test_name = example.evidence.partition("::")
        assert separator == "::", example
        path = ROOT / relative_path
        assert path.is_file(), example
        assert f"def {test_name}(" in path.read_text(encoding="utf-8"), example


def test_every_deferred_manifest_entry_explains_the_scope_gap() -> None:
    for example in UPSTREAM_SPEC_EXAMPLES:
        if example.status == "deferred":
            assert example.evidence.strip(), example
