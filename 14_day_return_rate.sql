/*
Built for PostgreSQL 12.4

Schema:
purchases                 
+---------------+-----------+
| user_id       | int       |
| ts            | timestamp |
| product_id    | int       |
+---------------+-----------+


Challenge - calculate the proportion of customers who made a repeat purchase within 14 days after their first purchase.

Discovered the FILTER function in PostgreSQL, which I didn’t know existed. With it, came up with a cleaner solution using just two CTEs and grouping dates via MAX().
*/

with ranked as (
  SELECT
    user_id,
    ts,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ts) AS rn
  FROM purchases
),

onetwo as (
SELECT
  user_id, 
  MAX(CASE WHEN rn = 1 then ts END) as first_ts,
  MAX(CASE WHEN rn = 2 then ts END) as second_ts
FROM ranked
GROUP BY user_id
)

SELECT  
  count(user_id) as total_users,
  count(user_id) FILTER (
    WHERE second_ts < first_ts + INTERVAL '14 days'
  ) as second_buy,
  count(user_id) FILTER (
    WHERE second_ts < first_ts + INTERVAL '14 days'
  )/count(user_id)::float as return_rate_14d
FROM onetwo 


/*
-- Previous bastard of a solution built during live code challenge:

with flagged as (
SELECT 
  user_id, 
  ts, 
  lag(ts,1) OVER (partition by user_id ORDER by ts) as lag_ts,
  product_id, 
  row_number() OVER (partition by user_id order by ts) as purch_order
from purchases
),

flagged12 as (
SELECT 
  user_id, 
  ts,
  lag_ts,
  CASE
    when ts < lag_ts + INTERVAL '14 days' then 1
    else 0 end
  as flag_14
from flagged
where purch_order in (1,2)
order by user_id, ts
),

second_purchse as ( 
SELECT user_id, sum(flag_14) from flagged12
group by user_id
HAVING sum(flag_14) > 0
)

select 
count(distinct s.user_id)/COUNT(distinct p.user_id)::float
from purchases p, second_purchse s;
*/
