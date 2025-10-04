SELECT 
    u.username,
    u.email,
    up.first_name,
    up.last_name,
    up.phone,
    COUNT(*) as total_records
FROM users u
INNER JOIN user_profiles up ON u.id = up.user_id
WHERE u.is_active = true
{% if email_domain %}
AND u.email LIKE '%@{{ email_domain }}'
{% endif %}
GROUP BY u.id, u.username, u.email, up.first_name, up.last_name, up.phone
HAVING COUNT(*) > {{ min_count | default(value=0) }}
ORDER BY total_records DESC