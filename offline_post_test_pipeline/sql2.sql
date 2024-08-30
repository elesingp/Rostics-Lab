DROP TABLE your_model ON CLUSTER '{cluster}';  
CREATE TABLE your_model ON CLUSTER '{cluster}' ENGINE = Memory AS 
SELECT 
    stochasticLinearRegressionState(0.00001, 0.1, 15, 'Adam')(toInt32(IfNull(added_points_qnt, 0)/100), toInt32(IfNull(used_points_qnt, 0)/100), toInt32(order_value)/100) as state 
FROM digital_product_analytics.app_metric_events
WHERE toDate(event_datetime) >= toDate(date_sub(now(), 10)) AND event_name IN ('system_order_create_success')





