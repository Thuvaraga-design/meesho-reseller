
--1.	Monthly revenue by category 

select month, category, Round(sum(quantity*unit_price), 2) as revenue, count(*) as n_orders 
from orders 
group by month, category;

--2.	Region-wise total revenue and order count 
select r.region, sum(quantity*unit_price) as revenue, count(*) as orders_count
from orders o
join resellers r on o.reseller_id = r.reseller_id
group by r.region;

--3.	Top resellers by total spend 
select r.reseller_id, r.reseller_name, sum(o.quantity*o.unit_price) as revenue
from orders o
join resellers r on o.reseller_id = r.reseller_id
group by r.reseller_id
having revenue > 50000
order by revenue desc
limit 5;

--4.	Resellers who have never placed an order 
select r.reseller_id, r.reseller_name, r.region
from resellers r
left join orders o on r.reseller_id = o.reseller_id
where o.order_id is null;


/*
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
*/

--	Reseller order count and total orders for a specific reseller
select r.reseller_id, r.reseller_name, COUNT(*) as count_all, COUNT(o.order_id) as count_order_id
from resellers r
left join orders o on r.reseller_id = o.reseller_id
where r.reseller_id = 'RS024';

--5.	Average Order Value (AOV) for June, Delivered orders only 
select o.month, round(sum(o.quantity*o.unit_price)/count(*), 2) as average_order_value
from orders o
join resellers r on o.reseller_id = r.reseller_id
where o.status = 'Delivered'
group by o.month
having o.month = 'June';



