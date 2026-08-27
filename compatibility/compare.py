from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from trmnl_liquid import Environment

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "compatibility" / "cases.json"
RUBY_DIR = ROOT / "compatibility" / "ruby"


def ruby_render(case: dict[str, object]) -> dict[str, object]:
    payload = json.dumps(
        {"template": case["template"], "data": case.get("data", {})},
        ensure_ascii=False,
    )
    completed = subprocess.run(
        ["bundle", "exec", "ruby", "render.rb"],
        cwd=RUBY_DIR,
        input=payload + "\n",
        text=True,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        return {
            "ok": False,
            "oracle_process_error": completed.returncode,
            "stderr": completed.stderr.strip(),
        }
    return json.loads(completed.stdout.strip())


def python_render(case: dict[str, object]) -> dict[str, object]:
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
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    failures: list[tuple[str, dict[str, object], dict[str, object]]] = []

    for case in cases:
        ruby = ruby_render(case)
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
