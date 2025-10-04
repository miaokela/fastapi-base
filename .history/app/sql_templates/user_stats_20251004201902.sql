SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(up.id) as profile_count,
    u.created_at,
    CASE 
        WHEN u.is_active = true THEN '活跃'
        ELSE '非活跃'
    END as status
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.created_at BETWEEN '{{ date_from }}' AND '{{ date_to }}'
GROUP BY u.id, u.username, u.email, u.created_at, u.is_active
ORDER BY profile_count DESC, u.created_at DESC
LIMIT {{ limit }}