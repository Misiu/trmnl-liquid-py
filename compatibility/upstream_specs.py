"""Coverage manifest for every official TRMNL Liquid 0.8.2 RSpec example.

Status meanings:
- ``differential``: the exact supported example is rendered by Ruby 0.8.2 and Python
  and compared byte-for-byte in ``compatibility/compare.py``.
- ``property``: the example is nondeterministic, time-dependent, or tests a helper/
  storage API rather than deterministic rendered output; a focused Python test covers
  the same contract.
- ``deferred``: the example requires Rails/ActionView or full I18n behavior that is
  explicitly outside the first compatibility gate.

Official source directory:
https://github.com/usetrmnl/trmnl-liquid/tree/0.8.2/spec/trmnl/liquid
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CoverageStatus = Literal["differential", "property", "deferred"]


@dataclass(frozen=True)
class UpstreamSpecExample:
    spec: str
    example: str
    status: CoverageStatus
    evidence: str


D = "differential"
P = "property"
X = "deferred"

UPSTREAM_SPEC_EXAMPLES: tuple[UpstreamSpecExample, ...] = (
    # fallback_spec.rb
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers thousands", D, "upstream fallback delimiter thousands"),
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers millions", D, "upstream fallback delimiter millions"),
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers millions with dot and comma notation", D, "upstream fallback delimiter dot comma"),
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers string as number", D, "upstream fallback delimiter numeric string"),
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers nil as empty string", D, "upstream fallback delimiter nil"),
    UpstreamSpecExample("fallback_spec.rb", "number_with_delimiter: answers identical string when not a number", D, "upstream fallback delimiter invalid"),
    UpstreamSpecExample("fallback_spec.rb", "number_to_currency: answers USD with two digit cents", D, "upstream fallback currency usd two cents"),
    UpstreamSpecExample("fallback_spec.rb", "number_to_currency: answers USD without cents", D, "upstream fallback currency usd no cents"),
    UpstreamSpecExample("fallback_spec.rb", "number_to_currency: answers USD with four digit cents", D, "upstream fallback currency usd four cents"),
    UpstreamSpecExample("fallback_spec.rb", "number_to_currency: answers pounds with two digit cents", D, "upstream fallback currency pounds"),
    UpstreamSpecExample("fallback_spec.rb", "ordinalize: answers zeroth", P, "tests/test_upstream_properties.py::test_fallback_ordinalize_examples"),
    UpstreamSpecExample("fallback_spec.rb", "ordinalize: answers first", P, "tests/test_upstream_properties.py::test_fallback_ordinalize_examples"),
    UpstreamSpecExample("fallback_spec.rb", "ordinalize: answers tenth", P, "tests/test_upstream_properties.py::test_fallback_ordinalize_examples"),
    UpstreamSpecExample("fallback_spec.rb", "ordinalize: answers one hundredth", P, "tests/test_upstream_properties.py::test_fallback_ordinalize_examples"),
    UpstreamSpecExample("fallback_spec.rb", "pluralize: answers zero as plural", D, "upstream fallback plural zero"),
    UpstreamSpecExample("fallback_spec.rb", "pluralize: answers one as singular", D, "upstream fallback plural one"),
    UpstreamSpecExample("fallback_spec.rb", "pluralize: answers multiple (with no replacement) as plural", D, "upstream fallback plural multiple"),
    # filters_spec.rb
    UpstreamSpecExample("filters_spec.rb", "append_random: appends random number", P, "tests/test_upstream_properties.py::test_append_random_contract"),
    UpstreamSpecExample("filters_spec.rb", "days_ago: renders default format", P, "tests/test_upstream_properties.py::test_days_ago_examples"),
    UpstreamSpecExample("filters_spec.rb", "days_ago: renders with custom time zone", P, "tests/test_upstream_properties.py::test_days_ago_examples"),
    UpstreamSpecExample("filters_spec.rb", "days_ago: renders custom format", P, "tests/test_upstream_properties.py::test_days_ago_examples"),
    UpstreamSpecExample("filters_spec.rb", "group_by: supports group_by", D, "upstream filter group by"),
    UpstreamSpecExample("filters_spec.rb", "find_by: finds by name", D, "upstream filter find by name"),
    UpstreamSpecExample("filters_spec.rb", "find_by: answers fallback when not found", D, "upstream filter find fallback"),
    UpstreamSpecExample("filters_spec.rb", "markdown_to_html: answers HTML", D, "upstream filter markdown html"),
    UpstreamSpecExample("filters_spec.rb", "markdown_to_html: answers empty string when given no content", P, "tests/test_upstream_properties.py::test_markdown_none_contract"),
    UpstreamSpecExample("filters_spec.rb", "number_with_delimiter: answers comma delimiter", D, "upstream filter delimiter comma"),
    UpstreamSpecExample("filters_spec.rb", "number_with_delimiter: answers period delimiter", D, "upstream filter delimiter period"),
    UpstreamSpecExample("filters_spec.rb", "number_with_delimiter: answers space and comma", D, "upstream filter delimiter space comma"),
    UpstreamSpecExample("filters_spec.rb", "number_to_currency: answers USD", D, "upstream filter currency usd"),
    UpstreamSpecExample("filters_spec.rb", "number_to_currency: answers pounds", D, "upstream filter currency pounds"),
    UpstreamSpecExample("filters_spec.rb", "number_to_currency: answers pounds with period and comma", D, "upstream filter currency pounds period comma"),
    UpstreamSpecExample("filters_spec.rb", "number_to_currency: answers Krones", X, "Rails/I18n locale-aware currency formatting is deferred"),
    UpstreamSpecExample("filters_spec.rb", "number_to_currency: answers custom format", D, "upstream filter currency custom unit"),
    UpstreamSpecExample("filters_spec.rb", "l_word: answers Spanish translation", X, "full I18n translations are deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_word: answers Korean translation", X, "full I18n translations are deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers now as date/time", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers today as date/time", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers UNIX timestamp as date/time", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers short year and month", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers time using locale key", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "l_date: answers short year and month with Korean translation", X, "full I18n localization is deferred"),
    UpstreamSpecExample("filters_spec.rb", "map_to_i: answers characters as zeros", D, "upstream filter map characters"),
    UpstreamSpecExample("filters_spec.rb", "map_to_i: answers numbers as numbers", D, "upstream filter map numbers"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers plural when count is zero", D, "upstream filter plural zero"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers singular when count is one", D, "upstream filter plural one"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers plural when count is more than one", D, "upstream filter plural multiple"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers plural for complex word", X, "Rails inflection rules are deferred"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers singular for complex word", X, "Rails inflection rules are deferred"),
    UpstreamSpecExample("filters_spec.rb", "pluralize: answers plural for alternate pluralization", D, "upstream filter plural explicit"),
    UpstreamSpecExample("filters_spec.rb", "json: answers JSON", D, "upstream filter json"),
    UpstreamSpecExample("filters_spec.rb", "parse_json: answers JSON", D, "upstream filter parse json"),
    UpstreamSpecExample("filters_spec.rb", "sample: asnwers random number", P, "tests/test_upstream_properties.py::test_sample_contract"),
    UpstreamSpecExample("filters_spec.rb", "sample: asnwers random word", P, "tests/test_upstream_properties.py::test_sample_contract"),
    UpstreamSpecExample("filters_spec.rb", "where_exp: answers orignal template when expression isn't applicable", D, "upstream filter where non collection"),
    UpstreamSpecExample("filters_spec.rb", "where_exp: answers content which matches or condition", D, "upstream filter where or"),
    UpstreamSpecExample("filters_spec.rb", "where_exp: answers content which matches equation", D, "upstream filter where equation"),
    UpstreamSpecExample("filters_spec.rb", "ordinalize: answers now as date/time", P, "tests/test_upstream_properties.py::test_ordinalize_dynamic_date_contract"),
    UpstreamSpecExample("filters_spec.rb", "ordinalize: answers today as date/time", P, "tests/test_upstream_properties.py::test_ordinalize_dynamic_date_contract"),
    UpstreamSpecExample("filters_spec.rb", "ordinalize: answers UNIX timestamp as date/time", D, "upstream filter ordinal timestamp"),
    UpstreamSpecExample("filters_spec.rb", "ordinalize: asnwers day (long), month, day (short), and year", D, "upstream filter ordinal date"),
    UpstreamSpecExample("filters_spec.rb", "ordinalize: asnwers day (long), month, and data (short)", D, "upstream filter ordinal offset"),
    UpstreamSpecExample("filters_spec.rb", "qr_code: answers SVG with defaults", D, "upstream filter qr defaults"),
    UpstreamSpecExample("filters_spec.rb", "qr_code: answers SVG for size and 7% level", D, "upstream filter qr low correction"),
    UpstreamSpecExample("filters_spec.rb", "qr_code: answers SVG for size and invalid level", D, "upstream filter qr invalid correction"),
    UpstreamSpecExample("filters_spec.rb", "qr_code: answers SVG with width and height when view box is fixed (disabled)", D, "upstream filter qr fixed comma syntax"),
    # memory_system_spec.rb
    UpstreamSpecExample("memory_system_spec.rb", "register: registers name and body", P, "tests/test_upstream_properties.py::test_memory_system_examples"),
    UpstreamSpecExample("memory_system_spec.rb", "read_template_file: reads template", P, "tests/test_upstream_properties.py::test_memory_system_examples"),
    UpstreamSpecExample("memory_system_spec.rb", "read_template_file: fails with file system error when template can't be found", P, "tests/test_upstream_properties.py::test_memory_system_examples"),
    # template_tag_spec.rb
    UpstreamSpecExample("template_tag_spec.rb", "render: answers content for registered template", D, "upstream template registered render"),
    UpstreamSpecExample("template_tag_spec.rb", "render: answers content with template contents stripped", D, "upstream template definition output"),
    UpstreamSpecExample("template_tag_spec.rb", "render: answers error with invalid template name", D, "upstream template invalid name"),
    UpstreamSpecExample("template_tag_spec.rb", "render: answers error for undefined template", D, "upstream template missing"),
)

assert len(UPSTREAM_SPEC_EXAMPLES) == 73
