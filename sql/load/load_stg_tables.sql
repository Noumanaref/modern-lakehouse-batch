USE DATABASE LAKEHOUSE_DB;
USE SCHEMA GOLD;
USE ROLE ACCOUNTADMIN;

-- Clear out any data from previous batch runs
TRUNCATE TABLE stg_stock_prices;
TRUNCATE TABLE stg_company_profiles;

-- Load Stock Prices from the S3 External Stage
COPY INTO stg_stock_prices
FROM @silver_prices_stage
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*[.]parquet'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Load Company Profiles from the S3 External Stage
COPY INTO stg_company_profiles
FROM @silver_profiles_stage
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*[.]parquet'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Deduplicate stock prices to handle raw Delta Parquet history
CREATE OR REPLACE TABLE stg_stock_prices AS 
SELECT * FROM stg_stock_prices 
QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol, price_date ORDER BY ingested_at DESC) = 1;

-- Deduplicate company profiles to handle raw Delta Parquet history
CREATE OR REPLACE TABLE stg_company_profiles AS 
SELECT * FROM stg_company_profiles 
QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY ingested_at DESC) = 1;