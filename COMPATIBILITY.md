# Compatibility contract

The first compatibility target for `trmnl-liquid-py` is
[`usetrmnl/trmnl-liquid` 0.8.2](https://github.com/usetrmnl/trmnl-liquid/tree/0.8.2).
Features added after that tag are intentionally excluded until a later upstream
release is adopted.

## Required baseline

A supported behavior is considered compatible only when the same Liquid input
and JSON-compatible data produce the same rendered output in the Ruby 0.8.2
oracle and in `trmnl-liquid-py`. Known mismatches are release blockers.

The compatibility harness sends JSON Lines to one Ruby process pinned to
`trmnl-liquid=0.8.2` and compares results with the Python implementation. Ruby is
a development/CI oracle only and is never a runtime dependency of the Python
package.

The checked-in differential corpus includes fixed regression cases, generated
cases, coercion-heavy cases, deterministic date/time cases, template/error cases,
and exact examples derived from the upstream specifications. `README.md` contains
a generated compatibility report whose counts are validated against the same
checked-in sources by CI.

## Official upstream specification coverage

All 73 examples from the four official TRMNL Liquid 0.8.2 spec files are tracked
in `compatibility/upstream_specs.json`:

- [`fallback_spec.rb`](https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/fallback_spec.rb)
- [`filters_spec.rb`](https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/filters_spec.rb)
- [`memory_system_spec.rb`](https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/memory_system_spec.rb)
- [`template_tag_spec.rb`](https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/template_tag_spec.rb)

The manifest classifies every example by evidence type:

- **46 differential** examples are executed through both the Ruby 0.8.2 oracle and
  the Python implementation and require exact rendered-output equality.
- **16 property/API** examples verify behavior that is more appropriately expressed
  as Python unit or API-contract tests rather than serialized render cases.
- **11 deferred** examples require Rails/ActionView or full I18n behavior and are
  deliberately outside the `0.1.0` compatibility scope.

A missing manifest entry, a changed count, or a differential mismatch fails CI.
Deferred examples are explicit scope decisions and must not be counted as supported.

## Non-Rails baseline

Rails/ActionView and internationalization are deferred for the first release.
The baseline therefore exercises `trmnl-liquid`'s own fallback implementations.

`trmnl-liquid` 0.8.2 references `RailsHelpers` before defining it when Rails
support has not been loaded. This makes several filters render `Liquid error:
internal` instead of reaching the fallback branch. The oracle defines an empty
`TRMNL::Liquid::RailsHelpers` module so the upstream `respond_to?` checks are
false and the gem executes its own `Fallback` code. No fallback behavior is
reimplemented in the Ruby oracle.

This adapter is intentionally limited to the missing constant. Rails helpers,
translations, and locale data are not loaded.

## Behavioral adaptation policy

Ruby `trmnl-liquid` 0.8.2 is the compatibility reference, even where Ruby Liquid,
Ruby core types, Redcarpet, or RQRCode differ from the corresponding Python
libraries. Compatibility adapters must use documented/public Python extension
points where they exist. Private-method overrides, test-only output rewriting,
`xfail`-based mismatch hiding, and broad lint/type suppressions are not acceptable
compatibility mechanisms.

Important implementation areas link directly to their Ruby reference and relevant
Python/library API in source comments or docstrings. This includes Liquid parsing
and runtime errors, TRMNL inline templates, Ruby scalar coercion, Markdown,
`where_exp`, QR rendering, and date/time conversion.

## Release rule

`0.1.0` must not be published while any supported 0.8.2 behavior has a known
differential mismatch. The release gate also requires green CI on Python
3.11-3.14, a successful wheel/sdist build and Twine validation, and a smoke test
that installs and renders from the built wheel in a clean environment.

Publishing, tagging, and merging the release remain separate explicit actions.