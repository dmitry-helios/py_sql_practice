/*
Schema:

Table: Users
+----+------+
| ID | Name |
+----+------+
| 1  | Alex |
| 2  | Ben  |
| 3  | Celia|
| 4  | Dan  |
| 5  | Eileen |
+----+------+

Table: UserLabels
+--------+---------+-----------+------------+
| UserID | LabelID | LabelName | CreatedAt  |
+--------+---------+-----------+------------+
| 1      | 11      | bot_vk    | 2024-09-01 |
| 1      | 12      | bot_tg    | 2024-08-01 |
| 2      | 16      | website   | 2024-09-29 |
| 2      | 11      | bot_vk    | 2024-09-03 |
| 3      | 16      | website   | 2024-09-30 |
| 3      | 12      | bot_tg    | 2024-08-05 |
| 4      | 16      | website   | 2024-09-15 |
| 4      | 15      | Bot_tg    | 2024-08-01 |
| 5      | 13      | Bot_vk    | 2024-08-01 |
| 5      | 14      | botvk     | 2024-10-01 |
… (etc.)
+--------+---------+-----------+------------+

Task:
Write a SQL query that:
  1. Counts the number of unique LabelID values per user Name
     where LabelName contains 'bot' (case-insensitive).
  2. Includes only labels created on or after September 1, 2024.
  3. Outputs Name and the count, ordered by count descending.
*/


--	Считает уникальные LabelID по каждому Name, где LabelName содержит “bot” без регистра и CreatedAt не раньше 1 сентября 2024.
SELECT 
    U.Name,  
    COUNT(DISTINCT UL.LabelID) AS UniqueLabels
FROM Users U
JOIN UserLabels UL ON U.ID = UL.UserID
WHERE 
	LOWER(UL.LabelName) LIKE LOWER('%bot%')
	-- Ожидает, что CreatedAt - либо типа DATE, либо в ISO-формате
	AND UL.CreatedAt >= '2024-09-01'
GROUP BY U.Name
ORDER BY UniqueLabels DESC;
