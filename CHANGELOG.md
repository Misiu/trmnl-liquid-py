# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0 - unreleased

Initial public release target for the Python port of `usetrmnl/trmnl-liquid` 0.8.2.

### Added

- TRMNL-compatible `Environment` and one-shot `render()` API.
- Inline `{% template %}` definitions backed by an in-memory template system.
- TRMNL filter surface for the supported non-I18n 0.8.2 scope.
- Ruby Liquid lax filter argument syntax used by TRMNL templates.
- Redcarpet-compatible Markdown rendering implemented on Mistune public APIs.
- RQRCode-compatible SVG output and QR mask selection using public `qrcode` APIs.
- Ruby-compatible scalar coercion for fallback filters.
- Ruby-compatible runtime error rendering and nested block continuation semantics.
- Typed package support through PEP 561 `py.typed` metadata.

### Compatibility

- Ruby/Python exact differential corpus: 574 cases with 0 known supported-scope mismatches.
- All 73 official TRMNL Liquid 0.8.2 RSpec examples classified and tracked:
  - 46 exact differential examples,
  - 16 property/API contract examples,
  - 11 Rails/I18n examples explicitly deferred.
- CI coverage for Python 3.11, 3.12, 3.13, and 3.14.

### Deferred

- Rails/ActionView integration.
- Full I18n/localized `l_word` and `l_date` behavior.
- Features introduced after upstream `trmnl-liquid` 0.8.2.
