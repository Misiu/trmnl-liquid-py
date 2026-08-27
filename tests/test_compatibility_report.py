from __future__ import annotations

from compatibility.report import collect_metrics, render_report, updated_readme


def test_compatibility_metrics_match_current_corpus() -> None:
    metrics = collect_metrics()

    assert metrics.differential_cases == 462
    assert metrics.upstream_examples == 73
    assert metrics.upstream_differential_cases == 46
    assert metrics.upstream_property_examples == 16
    assert metrics.upstream_deferred_examples == 11


def test_readme_compatibility_report_is_current() -> None:
    from compatibility.report import README

    source = README.read_text(encoding="utf-8")
    assert source == updated_readme(source)


def test_report_does_not_claim_full_i18n_compatibility() -> None:
    report = render_report()

    assert "462/462" in report
    assert "62/73" in report
    assert "Deferred Rails/I18n upstream examples | **11**" in report
