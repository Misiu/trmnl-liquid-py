from __future__ import annotations

from trmnl_liquid import Environment
from trmnl_liquid.memory_system import MemorySystem


def test_template_tag_preserves_raw_liquid_source() -> None:
    env = Environment()
    source = """{% template exact %}
  {{- name -}}
{% assign value = "a" | append, "b" %}
{% comment %}keep {{ this }} source{% endcomment %}
{% endtemplate %}"""

    env.render(source)

    assert isinstance(env.loader, MemorySystem)
    assert env.loader.read_template_file("exact") == (
        '{{- name -}}\n'
        '{% assign value = "a" | append, "b" %}\n'
        "{% comment %}keep {{ this }} source{% endcomment %}"
    )


def test_template_tag_raw_body_is_parsed_only_when_rendered() -> None:
    env = Environment()
    env.render(
        '{% template exact %}{{ "a" | append, "b" }}{% endtemplate %}'
    )

    assert env.render("{% render 'exact' %}") == "ab"
