-- Generate alter table statements
USE INFORMATION_SCHEMA;
SELECT 
    CONCAT('ALTER TABLE `',
            TABLE_SCHEMA,
            '`.`',
            TABLE_NAME,
            '` encryption=\'Y\';') AS MySQLCMD
FROM
    TABLES
WHERE
    TABLE_SCHEMA = 'uci_mys_saodb_chatbot_p';
-- Copy above result and run

-- Verify
SELECT
    TABLE_SCHEMA, TABLE_NAME, CREATE_OPTIONS
FROM
    INFORMATION_SCHEMA.TABLES
WHERE
    CREATE_OPTIONS LIKE '%ENCRYPTION%';