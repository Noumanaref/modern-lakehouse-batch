use database LAKEHOUSE_DB;
use schema GOLD;

-- Dimension: Company (SCD Type 1)
CREATE TABLE IF NOT EXISTS LAKEHOUSE_DB.GOLD.dim_company (
    company_key         INT AUTOINCREMENT PRIMARY KEY,
    symbol              VARCHAR UNIQUE NOT NULL,
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
    updated_at          TIMESTAMP_NTZ
);

-- Dimension: Date (Static Pre-computed Calendar)
CREATE TABLE IF NOT EXISTS LAKEHOUSE_DB.GOLD.dim_date (
    date_key    INT PRIMARY KEY,
    full_date   DATE NOT NULL,
    day_of_week VARCHAR,
    month       INT,
    year        INT,
    is_weekend  BOOLEAN
);



-- Fact: Stock Prices
CREATE TABLE IF NOT EXISTS LAKEHOUSE_DB.GOLD.fact_stock_prices (
    price_key    INT AUTOINCREMENT PRIMARY KEY,
    company_key  INT NOT NULL REFERENCES LAKEHOUSE_DB.GOLD.dim_company(company_key),
    date_key     INT NOT NULL REFERENCES LAKEHOUSE_DB.GOLD.dim_date(date_key),
    open         DOUBLE,
    high         DOUBLE,
    low          DOUBLE,
    close        DOUBLE,
    volume       BIGINT,
    ingested_at  TIMESTAMP_NTZ
);
