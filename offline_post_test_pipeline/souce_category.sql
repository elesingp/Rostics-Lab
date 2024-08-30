SELECT
    city,
    round(avgIf(session_length, event_name = 'user_checkout_open')) as add_session_length,
    round(avg(session_length)) - add_session_length as checkout_length,
    round(avgIf(order_value/100, event_name = 'system_order_create_success'),2) as aov,
    count(event_name = 'user_checkout_open') / count(event_name = 'system_order_create_success') as checkout_cr,
    COUNT(*) as orders
FROM digital_product_analytics.app_metric_events AS t1
WHERE toDate(t1.event_datetime) >= '2024-08-21' AND toDate(t1.event_datetime) < '2024-08-22'
AND t1.event_name IN ('system_order_create_success', 'user_checkout_open') AND city is not NULL
GROUP BY city
ORDER BY orders DESC
LIMIT 100