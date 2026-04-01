-- Valid Hive SQL with common functions and variables
SELECT
    TO_DATE(order_date) AS order_date,
    user_id,
    SUM(order_amount) AS total_amount,
    COUNT(DISTINCT order_id) AS order_count,
    AVG(order_amount) AS avg_amount,
    CONCAT_WS('-', user_id, order_date) AS composite_key,
    NVL(discount_amount, 0) AS discount,
    CASE
        WHEN order_amount > 1000 THEN 'high'
        WHEN order_amount > 500 THEN 'medium'
        ELSE 'low'
    END AS order_tier
FROM order_table
WHERE
    dt = '${bizdate}'
    AND order_status = 'completed'
    AND order_amount > 0
GROUP BY
    TO_DATE(order_date),
    user_id
HAVING
    SUM(order_amount) > 100
ORDER BY
    order_date DESC,
    total_amount DESC
LIMIT 1000;
