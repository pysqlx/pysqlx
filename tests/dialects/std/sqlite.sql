-- create_table
CREATE TABLE [customers] (
[id] integer NOT NULL PRIMARY KEY AUTOINCREMENT,
[full name] nvarchar(50) NOT NULL,
[code] char(3),
[notes] text,
[is_active] boolean DEFAULT 1,
[joined] date,
[created] datetime,
[balance] decimal(10, 2),
[photo] blob,
[score] real,
[level] integer DEFAULT 0
)
-- create_table_keys
CREATE TABLE [orders] (
[id] integer NOT NULL,
[line] integer NOT NULL,
[customer_id] integer,
[total] real,
PRIMARY KEY ([id], [line]),
FOREIGN KEY ([customer_id]) REFERENCES [customers] ([id])
)
-- create_database
UnsupportedOperationError: database creation is not supported in SQLite
-- create_schema
UnsupportedOperationError: schema creation is not supported in SQLite
-- create_index
CREATE UNIQUE INDEX [by name] ON [customers] ([full name], [code])
-- drop_table
DROP TABLE [customers]
-- drop_database
UnsupportedOperationError: database dropping is not supported in SQLite
-- drop_schema
UnsupportedOperationError: schema dropping is not supported in SQLite
-- drop_index
DROP INDEX [by name]
-- exists_table
SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='customers'
-- exists_plain_table
SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='orders'
-- exists_database
UnsupportedOperationError: database checks are not supported in SQLite
-- exists_schema
UnsupportedOperationError: schema checks are not supported in SQLite
-- exists_index
SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='by name'
-- empty
SELECT COUNT(*) FROM [orders]
-- length
SELECT COUNT(*) FROM [orders]
-- truncate
DELETE FROM [orders]
-- insert
INSERT INTO [orders] ([id],
[line],
[customer_id],
[total]) VALUES (?, ?, ?, ?)
-- insert_columns
INSERT INTO [customers] ([full name],
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
DELETE FROM [orders] WHERE (([full name] = 'O''Brien') AND ([created] > '2024-01-02 03:04:05')) OR (([code] NOT IN ( 'a', 'b' )) AND ([id] NOT BETWEEN 1 AND 9))
-- delete ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
DELETE FROM [orders] WHERE (([full name] = ?) AND ([created] > ?)) OR (([code] NOT IN ( ?, ? )) AND ([id] NOT BETWEEN ? AND ?))
-- select
SELECT [id],
[line],
[customer_id],
[total] FROM [orders]
-- select_condition
SELECT [id],
[full name] FROM [customers] WHERE (([full name] = 'O''Brien') AND ([created] > '2024-01-02 03:04:05')) OR (([code] NOT IN ( 'a', 'b' )) AND ([id] NOT BETWEEN 1 AND 9))
-- select_condition ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
SELECT [id],
[full name] FROM [customers] WHERE (([full name] = ?) AND ([created] > ?)) OR (([code] NOT IN ( ?, ? )) AND ([id] NOT BETWEEN ? AND ?))
-- select_values
SELECT [id] FROM [customers] WHERE ((((((([full name] LIKE 'a%') AND ([code] IS NULL)) AND ([created] != '2024-01-02')) AND ([code] <= [full name])) AND ([id] >= 1.5)) AND ([full name] < 1)) AND ([code] = X'01ff')) AND ([full name] = NULL)
-- select_values ['a%', datetime.date(2024, 1, 2), 1.5, True, b'\x01\xff', None]
SELECT [id] FROM [customers] WHERE ((((((([full name] LIKE ?) AND ([code] IS NULL)) AND ([created] != ?)) AND ([code] <= [full name])) AND ([id] >= ?)) AND ([full name] < ?)) AND ([code] = ?)) AND ([full name] = ?)
-- select_top
SELECT [total] FROM [orders] LIMIT 5
-- select_sorted
SELECT [total] FROM [orders] ORDER BY [id] ASC,
[line] DESC,
[total] DESC
-- select_offset
SELECT [total] FROM [orders] ORDER BY [id] ASC LIMIT 5 OFFSET 10
-- select_offset_only
SELECT [total] FROM [orders] ORDER BY [id] DESC LIMIT -1 OFFSET 10
-- select_offset_unsorted
SELECT [total] FROM [orders] LIMIT -1 OFFSET 10
-- select_aggregates
SELECT [customer_id],
COUNT(*),
COUNT([total]),
SUM([total]),
AVG([total]),
MIN([total]),
MAX([total]) FROM [orders] GROUP BY [customer_id] ORDER BY [customer_id] ASC
-- select_join
SELECT [customers].[full name],
SUM([orders].[total]) FROM [orders] LEFT JOIN [customers] ON [orders].[customer_id] = [customers].[id] WHERE [orders].[total] > 10 GROUP BY [customers].[full name] ORDER BY [customers].[full name] DESC LIMIT 3
-- select_join [10]
SELECT [customers].[full name],
SUM([orders].[total]) FROM [orders] LEFT JOIN [customers] ON [orders].[customer_id] = [customers].[id] WHERE [orders].[total] > ? GROUP BY [customers].[full name] ORDER BY [customers].[full name] DESC LIMIT 3
-- select_distinct
SELECT DISTINCT [full name], [code] FROM [customers] WHERE [code] != 'x' ORDER BY [full name] ASC, [code] DESC
-- select_distinct ['x']
SELECT DISTINCT [full name], [code] FROM [customers] WHERE [code] != ? ORDER BY [full name] ASC, [code] DESC
-- union
SELECT [id] FROM (
SELECT [id] FROM [customers] WHERE [full name] = 'a'
) [customers]
UNION ALL
SELECT [customer_id] FROM (
SELECT [customer_id] FROM [orders] WHERE [total] > 1
) [orders]
ORDER BY
[id] DESC
-- union ['a', 1]
SELECT [id] FROM (
SELECT [id] FROM [customers] WHERE [full name] = ?
) [customers]
UNION ALL
SELECT [customer_id] FROM (
SELECT [customer_id] FROM [orders] WHERE [total] > ?
) [orders]
ORDER BY
[id] DESC
