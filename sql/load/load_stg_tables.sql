use database LAKEHOUSE_DB;
use schema GOLD;
use role accountadmin;

-- Clear out any data from previous batch runs
TRUNCATE TABLE stg_stock_prices;
TRUNCATE TABLE stg_company_profiles;


--  Load Stock Prices from the S3 External Stage
COPY INTO stg_stock_prices
FROM @silver_prices_stage
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*[.]parquet'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

select *
from stg_stock_prices;

--  Load Company Profiles from the S3 External Stage
COPY INTO stg_company_profiles
FROM @silver_profiles_stage
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*[.]parquet'
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE



