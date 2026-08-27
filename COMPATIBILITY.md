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

## Release rule

`0.1.0` must not be published while any supported 0.8.2 behavior has a known
differential mismatch. The initial `0.0.0` package metadata is deliberately not
a release candidate.
