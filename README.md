# trmnl-liquid-py

[![PyPI](https://img.shields.io/pypi/v/trmnl-liquid-py)](https://pypi.org/project/trmnl-liquid-py/)
[![Python](https://img.shields.io/pypi/pyversions/trmnl-liquid-py)](https://pypi.org/project/trmnl-liquid-py/)
[![CI](https://github.com/Misiu/trmnl-liquid-py/actions/workflows/ci.yml/badge.svg)](https://github.com/Misiu/trmnl-liquid-py/actions/workflows/ci.yml)
[![Compatibility](https://github.com/Misiu/trmnl-liquid-py/actions/workflows/compatibility.yml/badge.svg)](https://github.com/Misiu/trmnl-liquid-py/actions/workflows/compatibility.yml)

A Python compatibility layer for [`usetrmnl/trmnl-liquid`](https://github.com/usetrmnl/trmnl-liquid), targeting byte-for-byte compatible rendering for the supported TRMNL Liquid 0.8.2 surface.

> [!NOTE]
> The current compatibility target is `trmnl-liquid` **0.8.2** for the supported non-I18n surface. Rails/ActionView and full I18n behavior are intentionally deferred.

## Installation

[`trmnl-liquid-py` is available on PyPI](https://pypi.org/project/trmnl-liquid-py/):

```bash
python -m pip install trmnl-liquid-py
```

Python **3.11–3.14** is supported.

## Quick start

```python
from trmnl_liquid import Environment

env = Environment()
template = env.from_string("Hello {{ name }}!")
print(template.render(name="TRMNL"))
```

For one-shot rendering:

```python
from trmnl_liquid import render

html = render("{{ value | number_with_delimiter }}", value=1234567)
```

## Inline templates

TRMNL adds an inline `{% template %}` definition that can later be rendered with Liquid's `{% render %}` tag:

```liquid
{% template card %}
<div>{{ title }}</div>
{% endtemplate %}

{% render 'card', title: 'Status' %}
```

`trmnl-liquid-py` reproduces TRMNL 0.8.2's raw-body and template-storage semantics, including its exact `{% endtemplate %}` terminator behavior.

## TRMNL filters

The 0.1.0 compatibility surface includes:

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

Important TRMNL/Ruby syntax differences are preserved where required. For example, Ruby Liquid's lax filter syntax accepts a leading comma before the first filter argument:

```liquid
{{ value | qr_code, 11 }}
```

### Markdown

`markdown_to_html` reproduces the tested output of TRMNL 0.8.2's default Redcarpet 3.6.1 configuration using Mistune on Python.

```liquid
{{ markdown | markdown_to_html }}
```

### QR codes

`qr_code` renders the SVG shape expected from TRMNL's RQRCode-based implementation, including compatible QR mask selection/scoring behavior.

```liquid
{{ 'https://example.com' | qr_code: 11 }}
```

## Compatibility target

The baseline is exactly:

- `trmnl-liquid` **0.8.2**
- Python **3.11, 3.12, 3.13, 3.14**
- non-I18n behavior
- Rails/ActionView and full localized `l_word` / `l_date` behavior deferred
- features added after upstream 0.8.2 excluded until a later compatibility target is adopted

Ruby `trmnl-liquid` 0.8.2 is the reference implementation. Differences in parsing, coercion, formatting, Markdown rendering, QR generation, template behavior, error handling, or rendered output are treated as compatibility issues when they affect the supported scope.

<!-- compatibility-report:start -->
### Compatibility evidence

| Gate | Result |
| --- | ---: |
| Ruby 0.8.2 vs Python exact differential corpus | **574/574** |
| Known mismatches in the supported scope | **0** |
| Official TRMNL 0.8.2 RSpec examples mapped | **73/73** |
| Upstream examples covered by exact differential tests | **46** |
| Upstream examples covered by property/unit tests | **16** |
| Upstream examples covered in the initial non-I18n scope | **62/73** |
| Deferred Rails/I18n upstream examples | **11** |
| Python CI matrix | **3.11, 3.12, 3.13, 3.14** |
| Comparison | **exact rendered output** |

The `Compatibility` workflow runs the Ruby oracle first and fails on any mismatch. It then checks that this generated report still matches the checked-in corpus and upstream-spec manifest.
<!-- compatibility-report:end -->

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for the compatibility contract, upstream spec mapping, and Ruby oracle details.

## Development

Install the project with development dependencies, then run the normal quality gates:

```bash
python -m pip install -e . pytest ruff mypy build twine \
  types-python-dateutil==2.9.0.20260807 \
  types-qrcode==8.2.0.20260518
ruff check .
mypy src/trmnl_liquid
pytest
python -m build
twine check dist/*
```

The Ruby/Python differential suite additionally requires Ruby and the bundle in `compatibility/ruby`:

```bash
bundle install --gemfile compatibility/ruby/Gemfile
python compatibility/compare.py
python -m compatibility.report --check
```

## Release process

Releases are tag-driven. There is no manual publish workflow and no PyPI API token stored in GitHub.

1. Update `src/trmnl_liquid/__about__.py` and `CHANGELOG.md` in a normal PR.
2. Merge the PR to `main` and wait for both `CI` and `Compatibility` to pass on `main`.
3. Create and push a tag whose name is exactly the package version, for example `0.1.0`.
4. The `Release` workflow verifies that the tag equals `__version__` and points to a commit on `main`.
5. The workflow builds and validates the wheel/sdist, publishes them to PyPI through Trusted Publishing, and only after a successful PyPI publish creates the matching GitHub Release with the distributions attached.

A tag such as `v0.1.0` is intentionally invalid when `__version__ == "0.1.0"`.

## License

MIT. The repository license includes attribution for portions derived from `usetrmnl/trmnl-liquid`.
