USE DATABASE LAKEHOUSE_DB;
USE SCHEMA GOLD;

MERGE INTO dim_company AS target
USING (
    -- Deduplicate staging data: guarantee strictly one record per symbol
    SELECT 
        symbol,
        company_name,
        sector,
        industry,
        exchange,
        exchange_full_name,
        country,
        currency,
        ipo_date,
        cik,
        isin,
        cusip,
        ingested_at
    FROM (
        SELECT *, 
               ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY ingested_at DESC) AS rn
        FROM stg_company_profiles
    )
    WHERE rn = 1
) AS source
ON target.symbol = source.symbol
WHEN MATCHED THEN
    UPDATE SET 
        target.company_name       = source.company_name,
        target.sector             = source.sector,
        target.industry           = source.industry,
        target.exchange           = source.exchange,
        target.exchange_full_name = source.exchange_full_name,
        target.country            = source.country,
        target.currency           = source.currency,
        target.ipo_date           = source.ipo_date,
        target.cik                = source.cik,
        target.isin               = source.isin,
        target.cusip              = source.cusip,
        target.updated_at         = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (
        symbol, 
        company_name, 
        sector, 
        industry, 
        exchange, 
        exchange_full_name, 
        country, 
        currency, 
        ipo_date, 
        cik, 
        isin, 
        cusip, 
        updated_at
    )
    VALUES (
        source.symbol, 
        source.company_name, 
        source.sector, 
        source.industry, 
        source.exchange, 
        source.exchange_full_name, 
        source.country, 
        source.currency, 
        source.ipo_date, 
        source.cik, 
        source.isin, 
        source.cusip, 
        CURRENT_TIMESTAMP()
    );