-- SQL with intentional syntax errors for testing validation
SELECT
    user_id,
    user_name,
    email
FROM users
WHERE
    status = 'active
    AND created_at >= '2025-01-01'
    AND (email IS NOT NULL
GROUP BY user_id
ORDER BY created_at DESC;
