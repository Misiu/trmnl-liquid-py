from __future__ import annotations

from datetime import datetime

from trmnl_liquid import Environment
from trmnl_liquid.memory_system import MemorySystem


def render(template: str, **data: object) -> str:
    return Environment().render(template, **data)


def test_template_tag_registers_and_renders() -> None:
    template = """{% template my_template %}Hello, {{ name }}{% endtemplate %}
{% render 'my_template', name: 'world' %}
{% render 'my_template', name: name %}"""
    assert render(template, name="George").strip() == "Hello, world\nHello, George"


def test_template_tag_emits_nothing_and_strips_body() -> None:
    assert (
        render("abc {% template my_template %}  Hello, {{ name }}  {% endtemplate %} 123")
        == "abc  123"
    )


def test_template_tag_invalid_name_matches_upstream_error() -> None:
    assert render("{% template Danger! %}Hello{% endtemplate %}") == (
        'Liquid error: invalid template name "Danger!" - template names must contain only '
        "letters, numbers, underscores, and slashes"
    )


def test_missing_template_matches_upstream_error() -> None:
    assert render('{% render "bogus" %}') == "Liquid error: Template not found: bogus."


def test_memory_system_persists_for_environment_lifetime() -> None:
    env = Environment()
    env.render("{% template greeting %}Hello{% endtemplate %}")
    assert env.render("{% render 'greeting' %}") == "Hello"


def test_memory_system_register_and_read() -> None:
    system = MemorySystem()
    assert system.register("test", "A body.") == "A body."
    assert system.read_template_file("test") == "A body."


def test_days_ago_remains_date_filter_compatible() -> None:
    expected = datetime.utcnow().strftime("%Y-%m-%d")
    assert render('{{ 0 | days_ago: "Etc/UTC" | date: "%Y-%m-%d" }}') == expected


def test_group_by_matches_ruby_hash_output() -> None:
    collection = [
        {"name": "Ryan", "age": 35},
        {"name": "Sara", "age": 29},
        {"name": "Jimbob", "age": 29},
    ]
    assert render("{{ collection | group_by: 'age' }}", collection=collection) == (
        '{35=>[{"name"=>"Ryan", "age"=>35}], '
        '29=>[{"name"=>"Sara", "age"=>29}, {"name"=>"Jimbob", "age"=>29}]}'
    )


def test_find_by_matches_ruby_hash_output() -> None:
    collection = [{"name": "Ryan", "age": 35}]
    assert render("{{ collection | find_by: 'name', 'Ryan' }}", collection=collection) == (
        '{"name"=>"Ryan", "age"=>35}'
    )


def test_markdown_to_html_matches_upstream_example() -> None:
    markdown = "This is a *test* and [here's a link](https://test.io)."
    assert render("{{ markdown | markdown_to_html }}", markdown=markdown).strip() == (
        '<p>This is a <em>test</em> and <a href="https://test.io">here&#39;s a link</a>.</p>'
    )


def test_pluralize_fallback_compares_count_without_coercion() -> None:
    assert render('{{ "book" | pluralize: "1" }}') == "1 books"


def test_parse_json_direct_hash_output_matches_ruby() -> None:
    assert render("{{ data | parse_json }}", data='{"a":1,"b":"c"}') == (
        '{"a"=>1, "b"=>"c"}'
    )


def test_where_exp_returns_original_for_non_collection() -> None:
    assert render('{{ "test" | where_exp: "la", "le" }}') == "test"


def test_where_exp_matches_or_condition() -> None:
    towns = [{"id": 1, "label": "Boulder"}, {"id": 2, "label": "Bozeman"}]
    template = '{{ towns | where_exp: "town", "town.label == \'Boulder\' or town.id < 2" }}'
    assert render(template, towns=towns) == '{"id"=>1, "label"=>"Boulder"}'


def test_where_exp_matches_numeric_comparison() -> None:
    template = (
        '{% assign nums = "1,2,3,4,5" | split: "," | map_to_i %}'
        '{{ nums | where_exp: "n", "n >= 3" }}'
    )
    assert render(template) == "345"


def test_ordinalize_fixed_values() -> None:
    assert render(
        '{{ 1770134949 | ordinalize: "%A, %B <<ordinal_day>>, %Y" }}'
    ) == "Tuesday, February 3rd, 2026"
    assert render(
        '{{ "2025-10-02" | ordinalize: "%A, %B <<ordinal_day>>, %Y" }}'
    ) == "Thursday, October 2nd, 2025"
    assert render(
        '{{ "2025-12-31 16:50:38 -0400" | ordinalize: "%A, %b <<ordinal_day>>" }}'
    ) == "Wednesday, Dec 31st"


def test_qr_code_default_and_fixed_dimensions() -> None:
    responsive = render('{{ "Test" | qr_code }}')
    assert responsive.startswith('<?xml version="1.0" standalone="yes"?><svg ')
    assert 'version="1.1"' in responsive
    assert 'xmlns="http://www.w3.org/2000/svg"' in responsive
    assert 'xmlns:xlink="http://www.w3.org/1999/xlink"' in responsive
    assert 'xmlns:ev="http://www.w3.org/2001/xml-events"' in responsive
    assert 'shape-rendering="crispEdges"' in responsive
    assert 'class="qr-code"' in responsive
    assert 'viewBox="0 0 231 231"' in responsive

    fixed = render('{{ "Test" | qr_code: 11, "", "fixed" }}')
    assert 'width="231" height="231"' in fixed
    assert "viewBox=" not in fixed
