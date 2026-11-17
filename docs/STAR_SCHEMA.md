# Gold Star Schema

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_STOCK_PRICES : occurs_on
    DIM_COMPANY ||--o{ FACT_STOCK_PRICES : has_prices

    DIM_DATE {
        int date_key PK
        date full_date
        string day_of_week
        int month
        int year
        boolean is_weekend
    }
    DIM_COMPANY {
        int company_key PK
        string symbol UK
        string company_name
        string sector
        string industry
        string exchange
        string country
        string currency
        date ipo_date
        string cik
        string isin
        string cusip
        timestamp updated_at
    }
    FACT_STOCK_PRICES {
        int price_key PK
        int company_key FK
        int date_key FK
        decimal open
        decimal high
        decimal low
        decimal close
        bigint volume
        timestamp ingested_at
    }
```

**Grain:** one row = one company, one trading day.

## Integrity rules

- `fact_stock_prices.company_key` -> FK -> `dim_company.company_key` (NOT NULL)
- `fact_stock_prices.date_key` -> FK -> `dim_date.date_key` (NOT NULL)
- `dim_company.symbol` is UNIQUE and NOT NULL: the natural key shared by both APIs
- The fact table uses the surrogate `company_key` for join performance, not the natural key

## Load strategy

| Table | Strategy |
|---|---|
| dim_company | MERGE on `symbol` (SCD Type 1) |
| dim_date | Static, built once |
| fact_stock_prices | Stub missing companies, then MERGE on `(company_key, date_key)` |

See [ADR 2](DECISIONS.md#adr-2) and [ADR 6](DECISIONS.md#adr-6).
