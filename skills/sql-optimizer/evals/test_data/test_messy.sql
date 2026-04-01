-- Messy SQL with inconsistent formatting
SELECT user_id,user_name,   email,    created_at
FROM users WHERE status='active'
and    created_at>='2025-01-01'
  AND email IS NOT NULL
GROUP BY user_id,user_name,email,created_at
ORDER BY created_at   DESC
LIMIT 100;
