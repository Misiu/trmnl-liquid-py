from trmnl_liquid import Environment


def render(template: str, **data: object) -> str:
    return Environment().render(template, **data)


def test_number_with_delimiter() -> None:
    assert render("{{ 1234 | number_with_delimiter }}") == "1,234"
    assert render('{{ 1234.57 | number_with_delimiter: " ", "," }}') == "1 234,57"
    assert render('{{ value | number_with_delimiter }}', value=None) == ""
    assert render('{{ value | number_with_delimiter }}', value="asdf") == "asdf"


def test_number_to_currency_fallback() -> None:
    assert render("{{ 10420 | number_to_currency }}") == "$10,420.00"
    assert render('{{ 1234.57 | number_to_currency: "£", ".", "," }}') == "£1.234,57"
    assert render('{{ 10420 | number_to_currency: "$", ",", ".", 0 }}') == "$10,420"


def test_map_to_i_matches_ruby_string_conversion() -> None:
    assert render('{% assign nums = "12px,-4.5,x" | split: "," | map_to_i %}{{ nums }}') == "12-40"


def test_json_and_parse_json() -> None:
    assert render("{{ data | json }}", data=[{"a": 1, "b": "c"}, "d"]) == '[{"a":1,"b":"c"},"d"]'
    assert render('{% assign value = data | parse_json %}{{ value.a }}', data='{"a":1}') == "1"


def test_find_by_fallback() -> None:
    data = [{"name": "Ryan", "age": 35}]
    assert render("{{ data | find_by: 'name', 'missing', 'Not Found' }}", data=data) == "Not Found"


def test_pluralize_fallback() -> None:
    assert render('{{ "book" | pluralize: 0 }}') == "0 books"
    assert render('{{ "book" | pluralize: 1 }}') == "1 book"
    assert render('{{ "person" | pluralize: 4, plural: "humans" }}') == "4 humans"


def test_i18n_filters_use_upstream_fallback_without_i18n() -> None:
    assert render('{{ "today" | l_word: "es-ES" }}') == "custom_plugins.today"
    assert render('{{ "2025-01-11" | l_date: "%y %b" }}') == "2025-01-11"
