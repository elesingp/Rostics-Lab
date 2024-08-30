WITH (SELECT state FROM (
    SELECT 
        stochasticLinearRegressionState(0.0015, 0.2, 20, 'Adam')(toInt32(order_value)/100, toInt32(IfNull(product_qnt, 0)), toInt32(IfNull(session_length, 0))) as state 
    FROM digital_product_analytics.app_metric_events
    WHERE toDate(event_datetime) >= toDate(date_sub(now(), 10)) AND event_name IN ('system_order_create_success')
    AND IfNull(product_qnt, 0) < 15)
) AS model,
toInt8(evalMLMethod(model, toInt32(IfNull(product_qnt, 0)), toInt32(IfNull(session_length, 0)))) as predict
SELECT
    session_length,
    IfNull(product_qnt, 0) as product_qnt,
    order_value/100 as real,
    if(predict = 0, 1, predict) as pred,
    round(100*SUM(if(abs(pred-real) <= 30, 1, 0)) OVER() / COUNT(if(pred = real, 0, 1)) OVER(), 2) as accuracy
FROM digital_product_analytics.app_metric_events
WHERE toDate(event_datetime) = toDate(date_sub(now(), 1)) AND event_name IN ('system_order_create_success')
LIMIT 100