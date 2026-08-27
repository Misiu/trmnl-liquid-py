from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from coercion_cases import coercion_cases
from date_time_cases import date_time_cases
from generated_cases import generated_cases
from template_error_cases import template_error_cases
from upstream_cases import upstream_differential_cases

from trmnl_liquid import Environment

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "compatibility" / "cases.json"
RUBY_DIR = ROOT / "compatibility" / "ruby"


def load_differential_cases() -> list[dict[str, Any]]:
    """Load all exact Ruby/Python compatibility cases."""
    fixed_cases: list[dict[str, Any]] = json.loads(CASES.read_text(encoding="utf-8"))
    return (
        fixed_cases
        + generated_cases()
        + coercion_cases()
        + date_time_cases()
        + template_error_cases()
        + upstream_differential_cases()
    )


def ruby_render_all(cases: list[dict[str, Any]]) -> list[dict[str, object]]:
    payload = "".join(
        json.dumps(
            {"template": case["template"], "data": case.get("data", {})},
            ensure_ascii=False,
        )
        + "\n"
        for case in cases
    )
    completed = subprocess.run(
        ["bundle", "exec", "ruby", "render.rb"],
        cwd=RUBY_DIR,
        input=payload,
        text=True,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        error = {
            "ok": False,
            "oracle_process_error": completed.returncode,
            "stderr": completed.stderr.strip(),
        }
        return [error.copy() for _ in cases]

    outputs = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    if len(outputs) != len(cases):
        error = {
            "ok": False,
            "oracle_protocol_error": f"expected {len(cases)} results, got {len(outputs)}",
            "stderr": completed.stderr.strip(),
        }
        return [error.copy() for _ in cases]
    return outputs


def python_render(case: dict[str, Any]) -> dict[str, object]:
    try:
        template = Environment().from_string(str(case["template"]))
        output = template.render(case.get("data", {}))
    except Exception as error:
        return {
            "ok": False,
            "error_class": type(error).__name__,
            "error": str(error),
        }
    return {"ok": True, "output": output}


def main() -> int:
    cases = load_differential_cases()
    ruby_results = ruby_render_all(cases)
    failures: list[tuple[str, dict[str, object], dict[str, object]]] = []

    for case, ruby in zip(cases, ruby_results, strict=True):
        python = python_render(case)
        name = str(case["name"])
        if ruby != python:
            failures.append((name, ruby, python))
            print(f"FAIL {name}")
            print(f"  ruby:   {ruby!r}")
            print(f"  python: {python!r}")
        else:
            print(f"PASS {name}")

    print(f"\nCompatibility: {len(cases) - len(failures)}/{len(cases)} cases")
    if failures:
        print(f"Mismatches: {len(failures)}")
        return 1
    print("Mismatches: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
