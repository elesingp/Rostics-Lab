
        SELECT
            studentTTest(aov, sample_index) as aov_stat, 
studentTTest(acs, sample_index) as acs_stat
        FROM (
        SELECT 
            0 as sample_index,
            t1.order_value as aov, 
t1.product_qnt as acs
        FROM digital_product_analytics.app_metric_events AS t1
        WHERE t1.event_name IN ('system_order_create_success') AND 
        toDate(t1.event_datetime) >= '2024-08-20' AND toDate(t1.event_datetime) < '2024-08-21'
        LIMIT 10000
        UNION ALL 
        SELECT 
            1 as sample_index,
            t1.order_value as aov, 
t1.product_qnt as acs
        FROM digital_product_analytics.app_metric_events AS t1
        toDate(t1.event_datetime) >= '2024-08-21' AND toDate(t1.event_datetime) < '2024-08-22'
        LIMIT 10000
        )