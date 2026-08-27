# trmnl-liquid-py

A Python port of [`usetrmnl/trmnl-liquid`](https://github.com/usetrmnl/trmnl-liquid), targeting byte-for-byte compatible rendering for the supported TRMNL Liquid surface.

> [!NOTE]
> This project is under active development. The initial compatibility target is `trmnl-liquid` **0.8.2**. Internationalization/Rails extensions are intentionally deferred.
>
> The package has not been released to PyPI yet. A release will only be prepared after the compatibility work is complete and explicitly approved.

## Why this package exists

[`python-liquid`](https://github.com/jg-rp/liquid) provides the Python Liquid parser and rendering engine. TRMNL's Ruby package adds behavior on top of standard Liquid that TRMNL templates rely on. `trmnl-liquid-py` provides that TRMNL-specific compatibility layer for Python.

The goal is not to create another general-purpose Liquid implementation. The goal is to make templates written for `trmnl-liquid` 0.8.2 render the same way in Python for the supported non-I18n surface.

## What this adds over python-liquid

For the `trmnl-liquid` 0.8.2 compatibility target, this package adds or adapts the following TRMNL-specific behavior on top of `python-liquid`:

### TRMNL tag behavior

- `{% template ... %}` definitions compatible with TRMNL's in-memory template/snippet behavior and subsequent `{% render ... %}` usage.

### TRMNL filters

- `append_random`
- `days_ago`
- `group_by`
- `find_by`
- `markdown_to_html`
- `number_with_delimiter`
- `number_to_currency`
- `l_word` fallback behavior
- `l_date` fallback behavior
- `map_to_i`
- `pluralize`
- `json`
- `parse_json`
- `sample`
- `where_exp`
- `ordinalize`
- `qr_code`

Where `python-liquid` already provides related Liquid functionality, `trmnl-liquid-py` still treats Ruby `trmnl-liquid` 0.8.2 as the compatibility reference. Differences in parsing, coercion, formatting, error handling, or rendered output are corrected in this package when they affect the supported TRMNL surface.

## Compatibility target

The initial baseline is exactly:

- `trmnl-liquid` **0.8.2**
- non-I18n behavior
- Ruby/Rails internationalization extensions are intentionally excluded from the first compatibility gate

Features added to upstream after 0.8.2 are not included until we intentionally adopt a newer upstream release.

Compatibility is verified with differential tests that render the same cases using the Ruby package and this Python implementation. Known mismatches in the supported surface are release blockers.

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for the compatibility contract and details of the Ruby reference runner.
