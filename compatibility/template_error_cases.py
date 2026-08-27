"""Deterministic template/render/runtime-error differential cases."""

from __future__ import annotations

from typing import Any


def template_error_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [
        {
            "name": "template edge stripped body whitespace",
            "template": (
                "{% template card %}\n\n  Hello {{ value }}  \n\n{% endtemplate %}"
                "{% render 'card', value: 'X' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge body preserves liquid source",
            "template": (
                "{% template card %}{% assign x = value | append: '!' %}{{ x }}"
                "{% endtemplate %}{% render 'card', value: 'Hi' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge duplicate definition last wins",
            "template": (
                "{% template card %}one{% endtemplate %}"
                "{% template card %}two{% endtemplate %}{% render 'card' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge render before definition",
            "template": (
                "A{% render 'late' %}B{% template late %}late{% endtemplate %}"
                "C{% render 'late' %}D"
            ),
            "data": {},
        },
        {
            "name": "template edge render same template twice",
            "template": (
                "{% template card %}[{{ value }}]{% endtemplate %}"
                "{% render 'card', value: 'A' %}{% render 'card', value: 'B' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge slash name",
            "template": (
                "{% template folder/card_2 %}ok{% endtemplate %}"
                "{% render 'folder/card_2' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge name surrounding whitespace",
            "template": (
                "{% template    card_1    %}ok{% endtemplate %}"
                "{% render 'card_1' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge empty name",
            "template": "X{% template %}body{% endtemplate %}Y",
            "data": {},
        },
        {
            "name": "template edge unicode name invalid",
            "template": "{% template żółw %}body{% endtemplate %}",
            "data": {},
        },
        {
            "name": "template edge invalid slash punctuation",
            "template": "{% template folder/card-name %}body{% endtemplate %}",
            "data": {},
        },
        {
            "name": "template edge render named arguments",
            "template": (
                "{% template card %}{{ a }}|{{ b }}|{{ c }}{% endtemplate %}"
                "{% render 'card', a: 1, b: 'x', c: true %}"
            ),
            "data": {},
        },
        {
            "name": "template edge render argument from parent",
            "template": (
                "{% template card %}{{ value }}{% endtemplate %}"
                "{% assign outer = 'parent' %}{% render 'card', value: outer %}"
            ),
            "data": {},
        },
        {
            "name": "template edge render isolates unpassed parent local",
            "template": (
                "{% template card %}[{{ outer }}]{% endtemplate %}"
                "{% assign outer = 'parent' %}{% render 'card' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge render local assignment does not leak",
            "template": (
                "{% template card %}{% assign inner = 'inside' %}{{ inner }}"
                "{% endtemplate %}{% render 'card' %}[{{ inner }}]"
            ),
            "data": {},
        },
        {
            "name": "template edge missing render inline",
            "template": "before:{% render 'missing' %}:after",
            "data": {},
        },
        {
            "name": "template edge missing render in true if",
            "template": "A{% if true %}B{% render 'missing' %}C{% endif %}D",
            "data": {},
        },
        {
            "name": "template edge missing render in false if",
            "template": "A{% if false %}{% render 'missing' %}{% endif %}B",
            "data": {},
        },
        {
            "name": "template edge missing render in loop",
            "template": (
                "{% for x in values %}[{{ x }}:{% render 'missing' %}]"
                "{% endfor %}"
            ),
            "data": {"values": [1, 2]},
        },
        {
            "name": "runtime error output node continues",
            "template": "A{{ values | map_to_i }}B{{ 2 }}C",
            "data": {"values": [True, False]},
        },
        {
            "name": "runtime error assign blank node",
            "template": (
                "A{% assign converted = values | map_to_i %}B{{ converted }}C"
            ),
            "data": {"values": [True, False]},
        },
        {
            "name": "runtime error output in true if",
            "template": "A{% if true %}B{{ values | map_to_i }}C{% endif %}D",
            "data": {"values": [True, False]},
        },
        {
            "name": "runtime error output in loop",
            "template": (
                "{% for x in values %}[{{ bad | map_to_i }}:{{ x }}]"
                "{% endfor %}"
            ),
            "data": {"values": [1, 2], "bad": [True]},
        },
        {
            "name": "runtime error inside rendered template",
            "template": (
                "{% template card %}A{{ bad | map_to_i }}B{% endtemplate %}"
                "X{% render 'card', bad: bad %}Y"
            ),
            "data": {"bad": [True]},
        },
        {
            "name": "runtime error assign inside rendered template",
            "template": (
                "{% template card %}A{% assign x = bad | map_to_i %}B{{ x }}C"
                "{% endtemplate %}{% render 'card', bad: bad %}"
            ),
            "data": {"bad": [True]},
        },
        {
            "name": "template edge conditional definition true",
            "template": (
                "{% if true %}{% template card %}ok{% endtemplate %}{% endif %}"
                "{% render 'card' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge conditional definition false",
            "template": (
                "{% if false %}{% template card %}ok{% endtemplate %}{% endif %}"
                "{% render 'card' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge whitespace control around definition",
            "template": (
                "A   {%- template card -%}  X  {%- endtemplate -%}   B"
                "{% render 'card' %}C"
            ),
            "data": {},
        },
        {
            "name": "template edge whitespace control in body",
            "template": (
                "{% template card %}A {{- value -}} B{% endtemplate %}"
                "{% render 'card', value: 'X' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge comment and raw source",
            "template": (
                "{% template card %}{% comment %}hidden {{ value }}{% endcomment %}"
                "A{% raw %}{{ raw_value }}{% endraw %}B{% endtemplate %}"
                "{% render 'card', value: 'X' %}"
            ),
            "data": {},
        },
        {
            "name": "template edge body with multiline liquid",
            "template": (
                "{% template card %}{% if value\n  == 'x' %}yes{% else %}no"
                "{% endif %}{% endtemplate %}{% render 'card', value: 'x' %}"
            ),
            "data": {},
        },
    ]

    assert len(cases) == 30
    return cases
