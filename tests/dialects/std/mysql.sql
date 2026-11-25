-- create_table
CREATE TABLE `shop`.`customers` (
`id` bigint NOT NULL AUTO_INCREMENT,
`full name` varchar(50) NOT NULL,
`code` char(3),
`notes` longtext,
`is_active` boolean DEFAULT 1,
`joined` date,
`created` datetime,
`balance` decimal(10, 2),
`photo` longblob,
`score` float,
`level` tinyint DEFAULT 0,
PRIMARY KEY (`id`)
)
-- create_table_keys
CREATE TABLE `orders` (
`id` int NOT NULL,
`line` int NOT NULL,
`customer_id` bigint,
`total` double,
PRIMARY KEY (`id`, `line`),
FOREIGN KEY (`customer_id`) REFERENCES `shop`.`customers` (`id`)
)
-- create_database
CREATE DATABASE `shop`
-- create_schema
UnsupportedOperationError: schema owners are not supported in MySQL
-- create_index
CREATE UNIQUE INDEX `by name` ON `shop`.`customers` (`full name`, `code`)
-- drop_table
DROP TABLE `shop`.`customers`
-- drop_database
DROP DATABASE `shop`
-- drop_schema
DROP SCHEMA `sales`
-- drop_index
DROP INDEX `by name` ON `shop`.`customers`
-- exists_table
SELECT COUNT(*) FROM information_schema.tables WHERE table_name='customers' AND table_schema='shop'
-- exists_plain_table
SELECT COUNT(*) FROM information_schema.tables WHERE table_name='orders' AND table_schema=DATABASE()
-- exists_database
SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='shop'
-- exists_schema
SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='sales'
-- exists_index
SELECT COUNT(DISTINCT index_name) FROM information_schema.statistics WHERE index_name='by name' AND table_name='customers' AND table_schema='shop'
-- empty
SELECT COUNT(*) FROM `orders`
-- length
SELECT COUNT(*) FROM `orders`
-- truncate
TRUNCATE TABLE `orders`
-- insert
INSERT INTO `orders` (`id`,
`line`,
`customer_id`,
`total`) VALUES (%s, %s, %s, %s)
-- insert_columns
INSERT INTO `shop`.`customers` (`full name`,
`code`) VALUES (%s, %s)
-- update
UPDATE `orders`
SET `total`=%s
WHERE `id` = 3
-- update [3]
UPDATE `orders`
SET `total`=%s
WHERE `id` = %s
-- delete
DELETE FROM `orders` WHERE ((`full name` = 'O''Brien') AND (`created` > '2024-01-02 03:04:05')) OR ((`code` NOT IN ( 'a', 'b' )) AND (`id` NOT BETWEEN 1 AND 9))
-- delete ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
DELETE FROM `orders` WHERE ((`full name` = %s) AND (`created` > %s)) OR ((`code` NOT IN ( %s, %s )) AND (`id` NOT BETWEEN %s AND %s))
-- select
SELECT `id`,
`line`,
`customer_id`,
`total` FROM `orders`
-- select_condition
SELECT `id`,
`full name` FROM `shop`.`customers` WHERE ((`full name` = 'O''Brien') AND (`created` > '2024-01-02 03:04:05')) OR ((`code` NOT IN ( 'a', 'b' )) AND (`id` NOT BETWEEN 1 AND 9))
-- select_condition ["O'Brien", datetime.datetime(2024, 1, 2, 3, 4, 5), 'a', 'b', 1, 9]
SELECT `id`,
`full name` FROM `shop`.`customers` WHERE ((`full name` = %s) AND (`created` > %s)) OR ((`code` NOT IN ( %s, %s )) AND (`id` NOT BETWEEN %s AND %s))
-- select_values
SELECT `id` FROM `shop`.`customers` WHERE (((((((`full name` LIKE 'a%') AND (`code` IS NULL)) AND (`created` != '2024-01-02')) AND (`code` <= `full name`)) AND (`id` >= 1.5)) AND (`full name` < 1)) AND (`code` = X'01ff')) AND (`full name` = NULL)
-- select_values ['a%', datetime.date(2024, 1, 2), 1.5, True, b'\x01\xff', None]
SELECT `id` FROM `shop`.`customers` WHERE (((((((`full name` LIKE %s) AND (`code` IS NULL)) AND (`created` != %s)) AND (`code` <= `full name`)) AND (`id` >= %s)) AND (`full name` < %s)) AND (`code` = %s)) AND (`full name` = %s)
-- select_top
SELECT `total` FROM `orders` LIMIT 5
-- select_sorted
SELECT `total` FROM `orders` ORDER BY `id` ASC,
`line` DESC,
`total` DESC
-- select_offset
SELECT `total` FROM `orders` ORDER BY `id` ASC LIMIT 5 OFFSET 10
-- select_offset_only
SELECT `total` FROM `orders` ORDER BY `id` DESC LIMIT 18446744073709551615 OFFSET 10
-- select_offset_unsorted
SELECT `total` FROM `orders` LIMIT 18446744073709551615 OFFSET 10
-- select_aggregates
SELECT `customer_id`,
COUNT(*),
COUNT(`total`),
SUM(`total`),
AVG(`total`),
MIN(`total`),
MAX(`total`) FROM `orders` GROUP BY `customer_id` ORDER BY `customer_id` ASC
-- select_join
SELECT `shop`.`customers`.`full name`,
SUM(`orders`.`total`) FROM `orders` LEFT JOIN `shop`.`customers` ON `orders`.`customer_id` = `shop`.`customers`.`id` WHERE `orders`.`total` > 10 GROUP BY `shop`.`customers`.`full name` ORDER BY `shop`.`customers`.`full name` DESC LIMIT 3
-- select_join [10]
SELECT `shop`.`customers`.`full name`,
SUM(`orders`.`total`) FROM `orders` LEFT JOIN `shop`.`customers` ON `orders`.`customer_id` = `shop`.`customers`.`id` WHERE `orders`.`total` > %s GROUP BY `shop`.`customers`.`full name` ORDER BY `shop`.`customers`.`full name` DESC LIMIT 3
-- select_distinct
SELECT DISTINCT `full name`, `code` FROM `shop`.`customers` WHERE `code` != 'x' ORDER BY `full name` ASC, `code` DESC
-- select_distinct ['x']
SELECT DISTINCT `full name`, `code` FROM `shop`.`customers` WHERE `code` != %s ORDER BY `full name` ASC, `code` DESC
-- union
SELECT `id` FROM (
SELECT `id` FROM `shop`.`customers` WHERE `full name` = 'a'
) `customers`
UNION ALL
SELECT `customer_id` FROM (
SELECT `customer_id` FROM `orders` WHERE `total` > 1
) `orders`
ORDER BY
`id` DESC
-- union ['a', 1]
SELECT `id` FROM (
SELECT `id` FROM `shop`.`customers` WHERE `full name` = %s
) `customers`
UNION ALL
SELECT `customer_id` FROM (
SELECT `customer_id` FROM `orders` WHERE `total` > %s
) `orders`
ORDER BY
`id` DESC
