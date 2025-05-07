/*
Schema:

Table: users
+-------------+-----------+
| Column      | Data Type |
+-------------+-----------+
| user_id     | integer   |
| installed_at| timestamp |
+-------------+-----------+

Table: payments
+-------------+-----------+
| Column      | Data Type |
+-------------+-----------+
| user_id     | integer   |
| payment_at  | timestamp |
| amount      | numeric   |
+-------------+-----------+

Given the tables above, write a SQL query to calculate cumulative ARPU
grouped by payment month, including only payments from users who installed
the app in January 2023.
*/

-- Берем только платежи установивших апп в январе 23, чтобы облегчить нагрузку
WITH jan23_user_payments AS (
    SELECT 
        p.payment_at,
        p.amount
    FROM payment p
    JOIN user u ON p.user_id = u.user_id
    WHERE u.installed_at >= '2023-01-01' AND u.installed_at < '2023-02-01'
),
-- Суммируем платежи по месяцам
monthly_revenue AS (
    SELECT 
        SUBSTR(payment_at, 1, 7) AS payment_month,
        SUM(amount) AS monthly_revenue
    FROM jan23_user_payments
    GROUP BY payment_month
),
-- Считаем накопленный итог
cumulative_revenue AS (
    SELECT 
        mr1.payment_month,
        mr1.monthly_revenue,
        SUM(mr2.monthly_revenue) AS total_cumulative_revenue
    FROM monthly_revenue mr1
    JOIN monthly_revenue mr2 ON mr2.payment_month <= mr1.payment_month
    GROUP BY mr1.payment_month, mr1.monthly_revenue
),
-- Посчитаем кол-во юзеров из января 23го один раз, чтобы не перегружать БД.
-- Используем CTE - не очень элегантно, но будет работать во всех DBMS. В постгре или MySQL использовали бы переменные.
jan23_user_count AS (
    SELECT COUNT(*) AS user_count
    FROM user
    WHERE installed_at >= '2023-01-01' AND installed_at < '2023-02-01'
)
-- Посчитаем накопленный ARPU по месяцам
SELECT 
    cr.payment_month AS month,
    cr.total_cumulative_revenue / uc.user_count AS cumulative_arpu
FROM cumulative_revenue cr
CROSS JOIN jan23_user_count uc
ORDER BY cr.payment_month;
