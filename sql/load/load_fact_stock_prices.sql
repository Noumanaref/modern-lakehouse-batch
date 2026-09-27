USE DATABASE LAKEHOUSE_DB;
USE SCHEMA GOLD;

MERGE INTO fact_stock_prices AS target
USING (
    SELECT 
        COALESCE(c.company_key, -1) AS company_key,
        TO_CHAR(s.price_date, 'YYYYMMDD')::INT AS date_key,
        s.open,
        s.high,
        s.low,
        s.close,
        s.volume,
        s.ingested_at
    FROM (
        SELECT *, 
               ROW_NUMBER() OVER (PARTITION BY symbol, price_date ORDER BY ingested_at DESC) AS rn
        FROM stg_stock_prices
    ) AS s
    LEFT JOIN dim_company c ON s.symbol = c.symbol
    WHERE s.rn = 1
) AS source
ON target.company_key = source.company_key 
   AND target.date_key = source.date_key
WHEN MATCHED THEN
    UPDATE SET 
        target.open = source.open,
        target.high = source.high,
        target.low = source.low,
        target.close = source.close,
        target.volume = source.volume,
        target.ingested_at = source.ingested_at
WHEN NOT MATCHED THEN
    INSERT (company_key, date_key, open, high, low, close, volume, ingested_at)
    VALUES (source.company_key, source.date_key, source.open, source.high, source.low, source.close, source.volume, source.ingested_at);