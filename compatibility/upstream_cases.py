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


def upstream_differential_cases() -> list[dict[str, Any]]:
    """Return deterministic supported upstream examples for Ruby/Python comparison."""
    cases: list[dict[str, Any]] = [
        # fallback_spec.rb -- number_with_delimiter
        {"name": "upstream fallback delimiter thousands", "template": "{{ 1234 | number_with_delimiter: ',', '.' }}", "data": {}},
        {"name": "upstream fallback delimiter millions", "template": "{{ 1234.567 | number_with_delimiter: ',', '.' }}", "data": {}},
        {"name": "upstream fallback delimiter dot comma", "template": "{{ 1234.567 | number_with_delimiter: '.', ',' }}", "data": {}},
        {"name": "upstream fallback delimiter numeric string", "template": "{{ value | number_with_delimiter: ',', '.' }}", "data": {"value": "1234.567"}},
        {"name": "upstream fallback delimiter nil", "template": "{{ value | number_with_delimiter: ',', '.' }}", "data": {"value": None}},
        {"name": "upstream fallback delimiter invalid", "template": "{{ value | number_with_delimiter: ',', '.' }}", "data": {"value": "asdf"}},
        # fallback_spec.rb -- number_to_currency
        {"name": "upstream fallback currency usd two cents", "template": "{{ 10420 | number_to_currency: '$', ',', '.', 2 }}", "data": {}},
        {"name": "upstream fallback currency usd no cents", "template": "{{ 10420 | number_to_currency: '$', ',', '.', 0 }}", "data": {}},
        {"name": "upstream fallback currency usd four cents", "template": "{{ 10420 | number_to_currency: '$', ',', '.', 4 }}", "data": {}},
        {"name": "upstream fallback currency pounds", "template": "{{ 1234.57 | number_to_currency: '£', '.', ',', 2 }}", "data": {}},
        # fallback_spec.rb -- ordinalize
        {"name": "upstream fallback ordinal zero", "template": "{{ 0 | ordinalize: '<<ordinal_day>>' }}", "data": {}},
        {"name": "upstream fallback ordinal one", "template": "{{ 1 | ordinalize: '<<ordinal_day>>' }}", "data": {}},
        {"name": "upstream fallback ordinal ten", "template": "{{ 10 | ordinalize: '<<ordinal_day>>' }}", "data": {}},
        {"name": "upstream fallback ordinal hundred", "template": "{{ 100 | ordinalize: '<<ordinal_day>>' }}", "data": {}},
        # fallback_spec.rb -- pluralize
        {"name": "upstream fallback plural zero", "template": "{{ 'cow' | pluralize: 0, plural: 'cows' }}", "data": {}},
        {"name": "upstream fallback plural one", "template": "{{ 'cow' | pluralize: 1, plural: 'cows' }}", "data": {}},
        {"name": "upstream fallback plural multiple", "template": "{{ 'cow' | pluralize: 2 }}", "data": {}},
        # filters_spec.rb
        {"name": "upstream filter group by", "template": "{{ collection | group_by: 'age' }}", "data": {"collection": [{"name": "Ryan", "age": 35}, {"name": "Sara", "age": 29}, {"name": "Jimbob", "age": 29}]}},
        {"name": "upstream filter find by name", "template": "{{ collection | find_by: 'name', 'Ryan' }}", "data": {"collection": [{"name": "Ryan", "age": 35}, {"name": "Sara", "age": 29}, {"name": "Jimbob", "age": 29}]}},
        {"name": "upstream filter find fallback", "template": "{{ collection | find_by: 'name', 'ronak', 'Not Found' }}", "data": {"collection": [{"name": "Ryan", "age": 35}, {"name": "Sara", "age": 29}, {"name": "Jimbob", "age": 29}]}},
        {"name": "upstream filter markdown html", "template": "{{ markdown | markdown_to_html }}", "data": {"markdown": "This is a *test* and [here's a link](https://test.io)."}},
        {"name": "upstream filter delimiter comma", "template": "{{ 1234 | number_with_delimiter }}", "data": {}},
        {"name": "upstream filter delimiter period", "template": "{{ 1234 | number_with_delimiter: '.' }}", "data": {}},
        {"name": "upstream filter delimiter space comma", "template": "{{ 1234.57 | number_with_delimiter: ' ', ',' }}", "data": {}},
        {"name": "upstream filter currency usd", "template": "{{ 10420 | number_to_currency }}", "data": {}},
        {"name": "upstream filter currency pounds", "template": "{{ 152350.69 | number_to_currency: '£' }}", "data": {}},
        {"name": "upstream filter currency pounds period comma", "template": "{{ 1234.57 | number_to_currency: '£', '.', ',' }}", "data": {}},
        {"name": "upstream filter currency custom unit", "template": "{{ 123 | number_to_currency: 'tbd' }}", "data": {}},
        {"name": "upstream filter map characters", "template": "{% assign nums = 'a, b, c, d, e' | split: ', ' | map_to_i %}{{ nums }}", "data": {}},
        {"name": "upstream filter map numbers", "template": "{% assign nums = '5, 4, 3, 2, 1' | split: ', ' | map_to_i %}{{ nums }}", "data": {}},
        {"name": "upstream filter plural zero", "template": "{{ 'book' | pluralize: 0 }}", "data": {}},
        {"name": "upstream filter plural one", "template": "{{ 'book' | pluralize: 1 }}", "data": {}},
        {"name": "upstream filter plural multiple", "template": "{{ 'book' | pluralize: 2 }}", "data": {}},
        {"name": "upstream filter plural explicit", "template": "{{ 'person' | pluralize: 4, plural: 'humans' }}", "data": {}},
        {"name": "upstream filter json", "template": "{{ data | json }}", "data": {"data": [{"a": 1, "b": "c"}, "d"]}},
        {"name": "upstream filter parse json", "template": "{% assign value = data | parse_json %}{{ value.a }}", "data": {"data": "{\"a\":1,\"b\":\"c\"}"}},
        {"name": "upstream filter where non collection", "template": "{{ 'test' | where_exp: 'la', 'le' }}", "data": {}},
        {"name": "upstream filter where or", "template": "{{ towns | where_exp: 'town', \"town.label == 'Boulder' or town.id < 2\" }}", "data": {"towns": [{"id": 1, "label": "Boulder"}, {"id": 2, "label": "Bozeman"}]}},
        {"name": "upstream filter where equation", "template": "{% assign nums = '1,2,3,4,5' | split: ',' | map_to_i %}{{ nums | where_exp: 'n', 'n >= 3' }}", "data": {}},
        {"name": "upstream filter ordinal timestamp", "template": "{{ 1770134949 | ordinalize: '%A, %B <<ordinal_day>>, %Y' }}", "data": {}},
        {"name": "upstream filter ordinal date", "template": "{{ '2025-10-02' | ordinalize: '%A, %B <<ordinal_day>>, %Y' }}", "data": {}},
        {"name": "upstream filter ordinal offset", "template": "{{ '2025-12-31 16:50:38 -0400' | ordinalize: '%A, %b <<ordinal_day>>' }}", "data": {}},
        {"name": "upstream filter qr defaults", "template": "{{ 'Test' | qr_code }}", "data": {}},
        {"name": "upstream filter qr low correction", "template": "{{ 'Test' | qr_code: 11, 'l' }}", "data": {}},
        {"name": "upstream filter qr invalid correction", "template": "{{ 'Test' | qr_code: 11, 'BOGUS' }}", "data": {}},
        {"name": "upstream filter qr fixed comma syntax", "template": "{{ 'Test' | qr_code, 11, '', 'fixed' }}", "data": {}},
        # template_tag_spec.rb
        {"name": "upstream template registered render", "template": "{% template my_template %}Hello, {{ name }}{% endtemplate %}\n{% render 'my_template', name: 'world' %}\n{% render 'my_template', name: name %}", "data": {"name": "George"}},
        {"name": "upstream template definition output", "template": "abc {% template my_template %}Hello, {{ name }}{% endtemplate %} 123", "data": {}},
        {"name": "upstream template invalid name", "template": "{% template Danger! %}Hello, world!{% endtemplate %}", "data": {}},
        {"name": "upstream template missing", "template": "{% render \"bogus\" %}", "data": {}},
    ]
    assert len(cases) == 50
    return cases
