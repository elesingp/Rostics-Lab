SELECT 
    --category_name,
    --countIf(event_name = 'system_product_showed' and screen_name = 'menu') as views,
    product_name,
    countIf(event_name = 'system_recommendations_showed' and 
        has(cat_prod_ids, '129716') = 1 or 
        has(cat_prod_ids, '276') = 1 or
        has(cat_prod_ids, '130321') = 1 or 
        has(cat_prod_ids, '130309') = 1 or 
        has(cat_prod_ids, '130299') = 1 or 
        has(cat_prod_ids, '130293') = 1 or 
        has(cat_prod_ids, '120') = 1 or 
        has(cat_prod_ids, '436') = 1 or 
        has(cat_prod_ids, '13') = 1 or 
        has(cat_prod_ids, '130315') = 1 or
        has(cat_prod_ids, '220') = 1 or 
        has(cat_prod_ids, '196') = 1
    ) as "souce_views(views)",
    countIf(event_name = 'user_product_added' 
            and screen_name = 'product_card'
            and (startsWith(product_name, 'Соус') = 0 and product_name != 'Кетчуп Томатный')
    ) as clicks,
    countIf(event_name = 'user_product_added' 
            and startsWith(source_code, 'product_card') = 1
            and (startsWith(product_name, 'Соус') = 1 or product_name = 'Кетчуп Томатный')
    ) as souce_clicks,
    countIf(event_name = 'user_product_removed'
            and (startsWith(product_name, 'Соус') = 1 or product_name = 'Кетчуп Томатный')
    ) as souce_remove,
    avgIf(price, event_name = 'user_product_added' 
            and startsWith(source_code, 'product_card') = 1
            and (startsWith(product_name, 'Соус') = 1 or product_name = 'Кетчуп Томатный')) as avg_price
FROM (
    SELECT 
        event_name,
        product_name,
        source_code,
        screen_name,
        price,
        category_name,
        arrayDistinct(
            arrayMap(x -> JSONExtractString(
                JSONExtractRaw(x, toString(indexOf(JSONExtractArrayRaw(recommendations), x) - 1)),
                'productId'
            ), JSONExtractArrayRaw(recommendations))
        ) as cat_prod_ids
    FROM app_metric_events
    WHERE toDate(event_datetime) >= toDate(date_sub(DAY, 1, now()))
)
WHERE category_name IN ('Сочная курица', 'Баскеты', 'Картофель и Снэки', 'Соусы')
AND event_name IN ('system_recommendations_showed', 'user_product_added', 'user_product_removed', 'system_product_showed')
GROUP BY product_name
ORDER BY "souce_views(views)" DESC
