use database LAKEHOUSE_DB;
use schema GOLD;

-- Transient Staging Table: Stock Prices
CREATE TRANSIENT TABLE IF NOT EXISTS LAKEHOUSE_DB.GOLD.stg_stock_prices (
    symbol      VARCHAR,
    price_date  DATE,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      BIGINT,
    ingested_at TIMESTAMP_NTZ
);

-- Transient Staging Table: company_profiles


CREATE TRANSIENT TABLE IF NOT EXISTS LAKEHOUSE_DB.GOLD.stg_company_profiles (
    symbol              VARCHAR,
    company_name        VARCHAR,
    sector              VARCHAR,
    industry            VARCHAR,
    exchange            VARCHAR,
    exchange_full_name  VARCHAR,
    country             VARCHAR,
    currency            VARCHAR,
    ipo_date            DATE,
    cik                 VARCHAR,
    isin                VARCHAR,
    cusip               VARCHAR,
    ingested_at         TIMESTAMP_NTZ
);