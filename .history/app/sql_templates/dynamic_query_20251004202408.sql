# 动态查询模板
SELECT {{ select | join(", ") }}
FROM {{ from }}
{% if joins %}
{% for join in joins %}
{{ join.type }} JOIN {{ join.table }} ON {{ join.on }}
{% endfor %}
{% endif %}
{% if where %}
WHERE
{% for condition in where %}
  {% if not loop.first %}{{ condition.logic }}{% endif %} 
  {% if condition.operator == "IN" %}
    {{ condition.field }} IN ({% for val in condition.value %}'{{ val }}'{% if not loop.last %}, {% endif %}{% endfor %})
  {% elif condition.operator == "BETWEEN" %}
    {{ condition.field }} BETWEEN '{{ condition.value.0 }}' AND '{{ condition.value.1 }}'
  {% elif condition.operator == "IS NULL" or condition.operator == "IS NOT NULL" %}
    {{ condition.field }} {{ condition.operator }}
  {% else %}
    {{ condition.field }} {{ condition.operator }} '{{ condition.value }}'
  {% endif %}
{% endfor %}
{% endif %}
{% if group_by %}
GROUP BY {{ group_by | join(", ") }}
{% endif %}
{% if having %}
HAVING
{% for condition in having %}
  {% if not loop.first %}AND{% endif %} {{ condition.field }} {{ condition.operator }} '{{ condition.value }}'
{% endfor %}
{% endif %}
{% if order_by %}
ORDER BY
{% for order in order_by %}
  {{ order.field }} {{ order.direction }}{% if not loop.last %}, {% endif %}
{% endfor %}
{% endif %}
{% if limit %}
LIMIT {{ limit }}
{% endif %}
{% if offset %}
OFFSET {{ offset }}
{% endif %}