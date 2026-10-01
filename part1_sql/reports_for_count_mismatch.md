Reports to demonstrate why COUNT(*) cannot be used to detect the zero-match case 

1. COUNT(*) counts that row → returns 1 (wrong, misleading)
2. COUNT(order_id) only counts non-NULL values of order_id → returns 0

In our database we have a specific seller with zero orders. Here is a query to identify the order count correctly using left join.

SELECT 
    r.reseller_id,
    r.reseller_name,
    COUNT(*) AS count_all, 
    COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o ON r.reseller_id = o.reseller_id
WHERE r.reseller_id = 'RS024' -- the specific reseller with zero orders

-- COUNT(*) AS count_all - counts all Rows in the resellers table
-- COUNT(o.order_id) AS count_order_id - counts only the rows that have a matching order_id in the orders table

Why this happens: COUNT(*) counts rows, regardless of content. Since the LEFT JOIN still produces one row (with NULLs) for the unmatched reseller, COUNT(*) sees "1 row exists" and reports 1 — even though there's no actual order. COUNT(column_name), on the other hand, only counts rows where that specific column is not NULL, so it correctly reports 0.