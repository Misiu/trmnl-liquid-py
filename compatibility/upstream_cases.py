"""Exact deterministic examples from TRMNL Liquid 0.8.2's upstream specs.

These cases intentionally mirror supported deterministic RSpec examples instead of
relying on nearby generated coverage. This gives the compatibility report an explicit,
auditable mapping to the upstream 0.8.2 contract.

Sources:
- https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/fallback_spec.rb
- https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/filters_spec.rb
- https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/spec/trmnl/liquid/template_tag_spec.rb
"""

from __future__ import annotations

from typing import Any


def _case(
    name: str,
    template: str,
    data: dict[str, object] | None = None,
) -> dict[str, Any]:
    return {"name": name, "template": template, "data": data or {}}


def upstream_differential_cases() -> list[dict[str, Any]]:
    """Return deterministic supported upstream examples for Ruby/Python comparison."""
    collection = [
        {"name": "Ryan", "age": 35},
        {"name": "Sara", "age": 29},
        {"name": "Jimbob", "age": 29},
    ]
    towns = [
        {"id": 1, "label": "Boulder"},
        {"id": 2, "label": "Bozeman"},
    ]

    cases = [
        # fallback_spec.rb -- number_with_delimiter
        _case(
            "upstream fallback delimiter thousands",
            "{{ 1234 | number_with_delimiter: ',', '.' }}",
        ),
        _case(
            "upstream fallback delimiter millions",
            "{{ 1234.567 | number_with_delimiter: ',', '.' }}",
        ),
        _case(
            "upstream fallback delimiter dot comma",
            "{{ 1234.567 | number_with_delimiter: '.', ',' }}",
        ),
        _case(
            "upstream fallback delimiter numeric string",
            "{{ value | number_with_delimiter: ',', '.' }}",
            {"value": "1234.567"},
        ),
        _case(
            "upstream fallback delimiter nil",
            "{{ value | number_with_delimiter: ',', '.' }}",
            {"value": None},
        ),
        _case(
            "upstream fallback delimiter invalid",
            "{{ value | number_with_delimiter: ',', '.' }}",
            {"value": "asdf"},
        ),
        # fallback_spec.rb -- number_to_currency
        _case(
            "upstream fallback currency usd two cents",
            "{{ 10420 | number_to_currency: '$', ',', '.', 2 }}",
        ),
        _case(
            "upstream fallback currency usd no cents",
            "{{ 10420 | number_to_currency: '$', ',', '.', 0 }}",
        ),
        _case(
            "upstream fallback currency usd four cents",
            "{{ 10420 | number_to_currency: '$', ',', '.', 4 }}",
        ),
        _case(
            "upstream fallback currency pounds",
            "{{ 1234.57 | number_to_currency: '£', '.', ',', 2 }}",
        ),
        # fallback_spec.rb -- pluralize
        _case(
            "upstream fallback plural zero",
            "{{ 'cow' | pluralize: 0, plural: 'cows' }}",
        ),
        _case(
            "upstream fallback plural one",
            "{{ 'cow' | pluralize: 1, plural: 'cows' }}",
        ),
        _case(
            "upstream fallback plural multiple",
            "{{ 'cow' | pluralize: 2 }}",
        ),
        # filters_spec.rb
        _case(
            "upstream filter group by",
            "{{ collection | group_by: 'age' }}",
            {"collection": collection},
        ),
        _case(
            "upstream filter find by name",
            "{{ collection | find_by: 'name', 'Ryan' }}",
            {"collection": collection},
        ),
        _case(
            "upstream filter find fallback",
            "{{ collection | find_by: 'name', 'ronak', 'Not Found' }}",
            {"collection": collection},
        ),
        _case(
            "upstream filter markdown html",
            "{{ markdown | markdown_to_html }}",
            {"markdown": "This is a *test* and [here's a link](https://test.io)."},
        ),
        _case(
            "upstream filter delimiter comma",
            "{{ 1234 | number_with_delimiter }}",
        ),
        _case(
            "upstream filter delimiter period",
            "{{ 1234 | number_with_delimiter: '.' }}",
        ),
        _case(
            "upstream filter delimiter space comma",
            "{{ 1234.57 | number_with_delimiter: ' ', ',' }}",
        ),
        _case(
            "upstream filter currency usd",
            "{{ 10420 | number_to_currency }}",
        ),
        _case(
            "upstream filter currency pounds",
            "{{ 152350.69 | number_to_currency: '£' }}",
        ),
        _case(
            "upstream filter currency pounds period comma",
            "{{ 1234.57 | number_to_currency: '£', '.', ',' }}",
        ),
        _case(
            "upstream filter currency custom unit",
            "{{ 123 | number_to_currency: 'tbd' }}",
        ),
        _case(
            "upstream filter map characters",
            "{% assign nums = 'a, b, c, d, e' | split: ', ' | map_to_i %}{{ nums }}",
        ),
        _case(
            "upstream filter map numbers",
            "{% assign nums = '5, 4, 3, 2, 1' | split: ', ' | map_to_i %}{{ nums }}",
        ),
        _case(
            "upstream filter plural zero",
            "{{ 'book' | pluralize: 0 }}",
        ),
        _case(
            "upstream filter plural one",
            "{{ 'book' | pluralize: 1 }}",
        ),
        _case(
            "upstream filter plural multiple",
            "{{ 'book' | pluralize: 2 }}",
        ),
        _case(
            "upstream filter plural explicit",
            "{{ 'person' | pluralize: 4, plural: 'humans' }}",
        ),
        _case(
            "upstream filter json",
            "{{ data | json }}",
            {"data": [{"a": 1, "b": "c"}, "d"]},
        ),
        _case(
            "upstream filter parse json",
            "{% assign value = data | parse_json %}{{ value.a }}",
            {"data": '{"a":1,"b":"c"}'},
        ),
        _case(
            "upstream filter where non collection",
            "{{ 'test' | where_exp: 'la', 'le' }}",
        ),
        _case(
            "upstream filter where or",
            "{{ towns | where_exp: 'town', \"town.label == 'Boulder' or town.id < 2\" }}",
            {"towns": towns},
        ),
        _case(
            "upstream filter where equation",
            "{% assign nums = '1,2,3,4,5' | split: ',' | map_to_i %}"
            "{{ nums | where_exp: 'n', 'n >= 3' }}",
        ),
        _case(
            "upstream filter ordinal timestamp",
            "{{ 1770134949 | ordinalize: '%A, %B <<ordinal_day>>, %Y' }}",
        ),
        _case(
            "upstream filter ordinal date",
            "{{ '2025-10-02' | ordinalize: '%A, %B <<ordinal_day>>, %Y' }}",
        ),
        _case(
            "upstream filter ordinal offset",
            "{{ '2025-12-31 16:50:38 -0400' | ordinalize: "
            "'%A, %b <<ordinal_day>>' }}",
        ),
        _case(
            "upstream filter qr defaults",
            "{{ 'Test' | qr_code }}",
        ),
        _case(
            "upstream filter qr low correction",
            "{{ 'Test' | qr_code: 11, 'l' }}",
        ),
        _case(
            "upstream filter qr invalid correction",
            "{{ 'Test' | qr_code: 11, 'BOGUS' }}",
        ),
        _case(
            "upstream filter qr fixed comma syntax",
            "{{ 'Test' | qr_code, 11, '', 'fixed' }}",
        ),
        # template_tag_spec.rb
        _case(
            "upstream template registered render",
            "{% template my_template %}Hello, {{ name }}{% endtemplate %}\n"
            "{% render 'my_template', name: 'world' %}\n"
            "{% render 'my_template', name: name %}",
            {"name": "George"},
        ),
        _case(
            "upstream template definition output",
            "abc {% template my_template %}Hello, {{ name }}{% endtemplate %} 123",
        ),
        _case(
            "upstream template invalid name",
            "{% template Danger! %}Hello, world!{% endtemplate %}",
        ),
        _case(
            "upstream template missing",
            '{% render "bogus" %}',
        ),
    ]
    assert len(cases) == 46
    return cases
