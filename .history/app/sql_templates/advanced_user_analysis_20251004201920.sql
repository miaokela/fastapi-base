-- 高级用户分析查询
SELECT 
    u.id,
    u.username,
    u.email,
    up.first_name,
    up.last_name,
    up.phone,
    u.is_active,
    u.is_superuser,
    u.created_at,
    u.last_login,
    DATE_PART('day', NOW() - u.last_login) as days_since_login,
    CASE
        WHEN u.last_login > NOW() - INTERVAL '7 days' THEN '本周活跃'
        WHEN u.last_login > NOW() - INTERVAL '30 days' THEN '本月活跃'
        WHEN u.last_login > NOW() - INTERVAL '90 days' THEN '季度活跃'
        ELSE '长期未活跃'
    END as activity_status
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE 1=1
{% if min_created_date %}
    AND u.created_at >= '{{ min_created_date }}'
{% endif %}
{% if max_created_date %}
    AND u.created_at <= '{{ max_created_date }}'
{% endif %}
{% if is_active is defined %}
    AND u.is_active = {{ is_active }}
{% endif %}
{% if email_domains %}
    AND (
    {% for domain in email_domains %}
        u.email LIKE '%@{{ domain }}'
        {% if not loop.last %}OR{% endif %}
    {% endfor %}
    )
{% endif %}
ORDER BY 
    u.last_login DESC NULLS LAST,
    u.created_at DESC
{% if limit %}
LIMIT {{ limit }}
{% endif %}