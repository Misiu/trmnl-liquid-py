"""Coverage manifest for every official TRMNL Liquid 0.8.2 RSpec example.

The data lives in ``upstream_specs.json`` so the manifest remains auditable without
embedding 73 long records in Python source.

Official source directory:
https://github.com/usetrmnl/trmnl-liquid/tree/0.8.2/spec/trmnl/liquid
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

CoverageStatus = Literal["differential", "property", "deferred"]


@dataclass(frozen=True)
class UpstreamSpecExample:
    spec: str
    example: str
    status: CoverageStatus
    evidence: str


_MANIFEST_PATH = Path(__file__).with_name("upstream_specs.json")
_VALID_STATUSES = {"differential", "property", "deferred"}


def load_upstream_spec_examples() -> tuple[UpstreamSpecExample, ...]:
    """Load and validate the checked-in upstream coverage manifest."""
    raw = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    examples: list[UpstreamSpecExample] = []

    if not isinstance(raw, list):
        raise ValueError("upstream_specs.json must contain a JSON array")

    for index, row in enumerate(raw):
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError(f"invalid upstream manifest row at index {index}")
        spec, example, status, evidence = row
        if not all(isinstance(value, str) for value in row):
            raise ValueError(f"non-string upstream manifest value at index {index}")
        if status not in _VALID_STATUSES:
            raise ValueError(f"invalid upstream manifest status at index {index}: {status}")
        examples.append(
            UpstreamSpecExample(
                spec=spec,
                example=example,
                status=cast(CoverageStatus, status),
                evidence=evidence,
            )
        )

    if len(examples) != 73:
        raise ValueError(f"expected 73 upstream examples, got {len(examples)}")
    return tuple(examples)


UPSTREAM_SPEC_EXAMPLES = load_upstream_spec_examples()
