-- create_table
CREATE TABLE [shop].[sales].[customers] (
[id] bigint NOT NULL IDENTITY(1, 1),
[full name] nvarchar(50) NOT NULL,
[code] char(3),
[notes] nvarchar(max),
[is_active] bit DEFAULT 1,
[joined] date,
[created] datetime,
[balance] decimal(10, 2),
[photo] varbinary(max),
[score] float(24),
[level] tinyint DEFAULT 0,
PRIMARY KEY ([id])
)
-- create_table_keys
CREATE TABLE [orders] (
[id] int NOT NULL,
[line] int NOT NULL,
[customer_id] bigint,
[total] float(53),
PRIMARY KEY ([id], [line]),
FOREIGN KEY ([customer_id]) REFERENCES [shop].[sales].[customers] ([id])
)
-- create_database
CREATE DATABASE [shop]
-- create_schema
CREATE SCHEMA [sales] AUTHORIZATION [me]
-- create_index
CREATE UNIQUE INDEX [by name] ON [shop].[sales].[customers] ([full name], [code])
-- drop_table
DROP TABLE [shop].[sales].[customers]
-- drop_database
DROP DATABASE [shop]
-- drop_schema
DROP SCHEMA [sales]
-- drop_index
DROP INDEX [by name] ON [shop].[sales].[customers]
-- exists_table
if exists (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'
    AND TABLE_NAME='customers')
    SELECT 1 AS result;
else
    SELECT 0 AS result;
-- exists_plain_table
if exists (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'
    AND TABLE_NAME='orders')
    SELECT 1 AS result;
else
    SELECT 0 AS result;
-- exists_database
if exists (
    SELECT name FROM master.sys.databases
    WHERE name='shop')
    SELECT 1 AS result;
else
    SELECT 0 AS result;
-- exists_schema
if exists (
    SELECT schema_name FROM information_schema.schemata
    WHERE schema_name='sales')
    SELECT 1 AS result;
else
    SELECT 0 AS result;
-- exists_index
if exists (
    SELECT 1 FROM sys.indexes WHERE name='by name'
    AND object_id=OBJECT_ID('[shop].[sales].[customers]'))
    SELECT 1 AS result;
else
    SELECT 0 AS result;
-- empty
SELECT COUNT(*) FROM [orders]
-- length
SELECT COUNT(*) FROM [orders]
-- truncate
TRUNCATE TABLE [orders]
-- insert
INSERT INTO [orders] ([id],
[line],
[customer_id],
[total]) VALUES (?, ?, ?, ?)
-- insert_columns
INSERT INTO [shop].[sales].[customers] ([full name],
[code]) VALUES (?, ?)
-- update
UPDATE [orders]
SET [total]=?
WHERE [id] = 3
-- update [3]
UPDATE [orders]
SET [total]=?
WHERE [id] = ?
-- delete
DELETE FROM [orders] WHERE (([full name] = 'O''Brien') AND ([created] > '2024-01-02T03:04:05.000')) OR (([code] NOT IN ( 'a', 'b' )) AND ([id] NOT BETWEEN 1 AND 9))
-- delete ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
DELETE FROM [orders] WHERE (([full name] = ?) AND ([created] > ?)) OR (([code] NOT IN ( ?, ? )) AND ([id] NOT BETWEEN ? AND ?))
-- select
SELECT [id],
[line],
[customer_id],
[total] FROM [orders]
-- select_condition
SELECT [id],
[full name] FROM [shop].[sales].[customers] WHERE (([full name] = 'O''Brien') AND ([created] > '2024-01-02T03:04:05.000')) OR (([code] NOT IN ( 'a', 'b' )) AND ([id] NOT BETWEEN 1 AND 9))
-- select_condition ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
SELECT [id],
[full name] FROM [shop].[sales].[customers] WHERE (([full name] = ?) AND ([created] > ?)) OR (([code] NOT IN ( ?, ? )) AND ([id] NOT BETWEEN ? AND ?))
-- select_values
SELECT [id] FROM [shop].[sales].[customers] WHERE ((((((([full name] LIKE 'a%') AND ([code] IS NULL)) AND ([created] != '2024-01-02')) AND ([code] <= [full name])) AND ([id] >= 1.5)) AND ([full name] < 1)) AND ([code] = 0x01ff)) AND ([full name] = NULL)
-- select_values ['a%', datetime.date(2024, 1, 2), 1.5, True, b'\x01\xff', None]
SELECT [id] FROM [shop].[sales].[customers] WHERE ((((((([full name] LIKE ?) AND ([code] IS NULL)) AND ([created] != ?)) AND ([code] <= [full name])) AND ([id] >= ?)) AND ([full name] < ?)) AND ([code] = ?)) AND ([full name] = ?)
-- select_top
SELECT TOP (5) [total] FROM [orders]
-- select_sorted
SELECT [total] FROM [orders] ORDER BY [id] ASC,
[line] DESC,
[total] DESC
-- select_offset
SELECT [total] FROM [orders] ORDER BY [id] ASC OFFSET 10 ROWS FETCH NEXT 5 ROWS ONLY
-- select_offset_only
SELECT [total] FROM [orders] ORDER BY [id] DESC OFFSET 10 ROWS
-- select_offset_unsorted
InvalidArgumentError: SQL Server needs ascend_by or descend_by to use offset
-- select_aggregates
SELECT [customer_id],
COUNT(*),
COUNT([total]),
SUM([total]),
AVG([total]),
MIN([total]),
MAX([total]) FROM [orders] GROUP BY [customer_id] ORDER BY [customer_id] ASC
-- select_join
SELECT TOP (3) [shop].[sales].[customers].[full name],
SUM([orders].[total]) FROM [orders] LEFT JOIN [shop].[sales].[customers] ON [orders].[customer_id] = [shop].[sales].[customers].[id] WHERE [orders].[total] > 10 GROUP BY [shop].[sales].[customers].[full name] ORDER BY [shop].[sales].[customers].[full name] DESC
-- select_join [10]
SELECT TOP (3) [shop].[sales].[customers].[full name],
SUM([orders].[total]) FROM [orders] LEFT JOIN [shop].[sales].[customers] ON [orders].[customer_id] = [shop].[sales].[customers].[id] WHERE [orders].[total] > ? GROUP BY [shop].[sales].[customers].[full name] ORDER BY [shop].[sales].[customers].[full name] DESC
-- select_having
SELECT [customer_id],
SUM([total]) FROM [orders] WHERE [total] > 1 GROUP BY [customer_id] HAVING ((SUM([total]) >= 10) AND (COUNT(*) != 2)) AND (AVG([total]) BETWEEN 1 AND 5) ORDER BY [customer_id] ASC
-- select_having [1, 10, 2, 1, 5]
SELECT [customer_id],
SUM([total]) FROM [orders] WHERE [total] > ? GROUP BY [customer_id] HAVING ((SUM([total]) >= ?) AND (COUNT(*) != ?)) AND (AVG([total]) BETWEEN ? AND ?) ORDER BY [customer_id] ASC
-- select_alias
SELECT [orders].[id],
[o 2].[id] FROM [orders] INNER JOIN [orders] [o 2] ON ([orders].[customer_id] = [o 2].[customer_id]) AND ([orders].[total] < [o 2].[total])
-- select_only_alias
SELECT TOP (1) [id] FROM [orders] [o 2]
-- reflect
SELECT c.column_name, c.data_type, c.character_maximum_length,
c.numeric_precision, c.numeric_scale, c.is_nullable, c.column_default,
(SELECT COUNT(*) FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage k ON k.constraint_name = tc.constraint_name
AND k.table_schema = tc.table_schema AND k.table_name = tc.table_name
WHERE tc.constraint_type = 'PRIMARY KEY' AND k.table_schema = c.table_schema
AND k.table_name = c.table_name AND k.column_name = c.column_name),
COLUMNPROPERTY(OBJECT_ID(QUOTENAME(c.table_schema) + '.' + QUOTENAME(c.table_name)), c.column_name, 'IsIdentity'), NULL
FROM information_schema.columns c
WHERE c.table_name = 'customers'
AND c.table_schema = 'sales'
ORDER BY c.ordinal_position
-- reflect_plain
SELECT c.column_name, c.data_type, c.character_maximum_length,
c.numeric_precision, c.numeric_scale, c.is_nullable, c.column_default,
(SELECT COUNT(*) FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage k ON k.constraint_name = tc.constraint_name
AND k.table_schema = tc.table_schema AND k.table_name = tc.table_name
WHERE tc.constraint_type = 'PRIMARY KEY' AND k.table_schema = c.table_schema
AND k.table_name = c.table_name AND k.column_name = c.column_name),
COLUMNPROPERTY(OBJECT_ID(QUOTENAME(c.table_schema) + '.' + QUOTENAME(c.table_name)), c.column_name, 'IsIdentity'), NULL
FROM information_schema.columns c
WHERE c.table_name = 'orders'
AND c.table_schema = SCHEMA_NAME()
ORDER BY c.ordinal_position
-- select_distinct
SELECT DISTINCT [full name], [code] FROM [shop].[sales].[customers] WHERE [code] != 'x' ORDER BY [full name] ASC, [code] DESC
-- select_distinct ['x']
SELECT DISTINCT [full name], [code] FROM [shop].[sales].[customers] WHERE [code] != ? ORDER BY [full name] ASC, [code] DESC
-- union
SELECT [id] FROM (
SELECT [id] FROM [shop].[sales].[customers] WHERE [full name] = 'a'
) [customers]
UNION ALL
SELECT [customer_id] FROM (
SELECT [customer_id] FROM [orders] WHERE [total] > 1
) [orders]
ORDER BY
[id] DESC
-- union ['a', 1]
SELECT [id] FROM (
SELECT [id] FROM [shop].[sales].[customers] WHERE [full name] = ?
) [customers]
UNION ALL
SELECT [customer_id] FROM (
SELECT [customer_id] FROM [orders] WHERE [total] > ?
) [orders]
ORDER BY
[id] DESC
-- foreign keys of orders
SELECT fk.name, pc.name,
CASE WHEN rt.schema_id = pt.schema_id THEN NULL ELSE SCHEMA_NAME(rt.schema_id) END,
rt.name, rc.name
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
JOIN sys.tables pt ON pt.object_id = fk.parent_object_id
JOIN sys.columns pc ON pc.object_id = fkc.parent_object_id
AND pc.column_id = fkc.parent_column_id
JOIN sys.tables rt ON rt.object_id = fkc.referenced_object_id
JOIN sys.columns rc ON rc.object_id = fkc.referenced_object_id
AND rc.column_id = fkc.referenced_column_id
WHERE fk.parent_object_id = OBJECT_ID('[orders]')
ORDER BY fk.name, fkc.constraint_column_id
-- foreign keys of customers
SELECT fk.name, pc.name,
CASE WHEN rt.schema_id = pt.schema_id THEN NULL ELSE SCHEMA_NAME(rt.schema_id) END,
rt.name, rc.name
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
JOIN sys.tables pt ON pt.object_id = fk.parent_object_id
JOIN sys.columns pc ON pc.object_id = fkc.parent_object_id
AND pc.column_id = fkc.parent_column_id
JOIN sys.tables rt ON rt.object_id = fkc.referenced_object_id
JOIN sys.columns rc ON rc.object_id = fkc.referenced_object_id
AND rc.column_id = fkc.referenced_column_id
WHERE fk.parent_object_id = OBJECT_ID('[shop].[sales].[customers]')
ORDER BY fk.name, fkc.constraint_column_id
