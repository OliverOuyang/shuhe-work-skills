-- =============================================================================
-- Query Name: User Analysis Report
-- Author: Data Team
-- Created: 2025-03-30
-- Description: Analyzes user registration and activity patterns
-- =============================================================================

-- Main query to fetch user data
SELECT
    user_id,           -- User unique identifier
    user_name,         -- User display name
    email,             -- User email address
    created_at,        -- Registration timestamp
    last_login_at      -- Last login timestamp
FROM users
WHERE
    -- Filter active users only
    status = 'active'
    -- Only users from 2025 onwards
    AND created_at >= '2025-01-01'
    -- Exclude users without email
    AND email IS NOT NULL
ORDER BY created_at DESC
LIMIT 100;

-- End of query
