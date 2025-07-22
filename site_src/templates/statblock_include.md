<!-- Reusable Stat Block Include Template -->
<!-- Use with the include-markdown plugin -->
<!-- Example usage: {%include 'templates/statblock_include.md' %}-->

> **{{ name }}**
> *{{ size }} {{ type }}, {{ alignment }}*
> 
> **Armor Class** {{ ac }} {% if ac_notes %}({{ ac_notes }}){% endif %}
> **Hit Points** {{ hp }} ({{ hp_formula }})
> **Speed** {{ speed }}
> 
> | STR     | DEX     | CON     | INT     | WIS     | CHA     |
> |---------|---------|---------|---------|---------|---------|
> | {{ str }} ({{ str_mod }}) | {{ dex }} ({{ dex_mod }}) | {{ con }} ({{ con_mod }}) | {{ int }} ({{ int_mod }}) | {{ wis }} ({{ wis_mod }}) | {{ cha }} ({{ cha_mod }}) |
> 
> {% if saves %}**Saving Throws** {{ saves }}{% endif %}
> {% if skills %}**Skills** {{ skills }}{% endif %}
> {% if damage_resistances %}**Damage Resistances** {{ damage_resistances }}{% endif %}
> {% if damage_immunities %}**Damage Immunities** {{ damage_immunities }}{% endif %}
> {% if condition_immunities %}**Condition Immunities** {{ condition_immunities }}{% endif %}
> **Senses** {{ senses }}
> **Languages** {{ languages }}
> **Challenge** {{ cr }} ({{ xp }} XP)
> 
> {% for trait in traits %}
> **{{ trait.name }}.** {{ trait.desc }}
> 
> {% endfor %}

### Actions

{% for action in actions %}
> **{{ action.name }}.** {% if action.attack %}*{{ action.attack.type }}:* {{ action.attack.tohit }} to hit, {{ action.attack.reach }}, {{ action.attack.target }}. *Hit:* {{ action.attack.damage }} {{ action.attack.damage_type }} damage.{% else %}{{ action.desc }}{% endif %}
> 
{% endfor %}

{% if bonus_actions %}
### Bonus Actions

{% for bonus in bonus_actions %}
> **{{ bonus.name }}.** {{ bonus.desc }}
> 
{% endfor %}
{% endif %}

{% if reactions %}
### Reactions

{% for reaction in reactions %}
> **{{ reaction.name }}.** {{ reaction.desc }}
> 
{% endfor %}
{% endif %}

{% if legendary_actions %}
### Legendary Actions

> The {{ name }} can take {{ legendary_actions_count }} legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The {{ name }} regains spent legendary actions at the start of its turn.
> 
{% for action in legendary_actions %}
> **{{ action.name }}{% if action.cost %} (Costs {{ action.cost }} Actions){% endif %}.** {{ action.desc }}
{% endfor %}
{% endif %}