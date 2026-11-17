# Problems Faced

## 1. Early-arriving fact (the TSLA problem)

**Situation.** Twelve Data delivers a price row for a brand-new symbol (TSLA) but FMP has not delivered its profile yet. `stg_stock_prices` has TSLA; `dim_company` does not.

| Attempt | What happens | Verdict |
|---|---|---|
| INNER JOIN | TSLA row silently dropped; the query "succeeds" | Data lost, no error |
| LEFT JOIN + `COALESCE(company_key, -1)` | Row kept but points at nothing; BI shows a blank or drops it | Problem moved downstream |
| Seed a `-1 'Unresolved Company'` row | Visible, but TSLA never gets a real identity | Patch |
| **Auto-stub (chosen)** | Create a real dim row first, then INNER JOIN is safe | Root-cause fix |

### Implemented solution

```sql
USE DATABASE LAKEHOUSE_DB;
USE SCHEMA GOLD;

-- STEP 1: auto-stub (inferred member pattern)
INSERT INTO dim_company (symbol, company_name, updated_at)
SELECT DISTINCT s.symbol, 'Pending Profile Sync', CURRENT_TIMESTAMP()
FROM stg_stock_prices s
LEFT JOIN dim_company c ON s.symbol = c.symbol
WHERE c.symbol IS NULL;

-- STEP 2: fact MERGE (strict INNER JOIN is now safe)
MERGE INTO fact_stock_prices AS target
USING (
    SELECT c.company_key,
           TO_CHAR(s.price_date, 'YYYYMMDD')::INT AS date_key,
           s.open, s.high, s.low, s.close, s.volume, s.ingested_at
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY symbol, price_date
                                  ORDER BY ingested_at DESC) AS rn
        FROM stg_stock_prices
    ) AS s
    INNER JOIN dim_company c ON s.symbol = c.symbol
    WHERE s.rn = 1
) AS source
ON  target.company_key = source.company_key
AND target.date_key    = source.date_key
WHEN MATCHED THEN UPDATE SET
    target.open = source.open, target.high = source.high,
    target.low = source.low, target.close = source.close,
    target.volume = source.volume, target.ingested_at = source.ingested_at
WHEN NOT MATCHED THEN INSERT
    (company_key, date_key, open, high, low, close, volume, ingested_at)
VALUES
    (source.company_key, source.date_key, source.open, source.high,
     source.low, source.close, source.volume, source.ingested_at);
```

### Walkthrough

1. **Arrival.** `dim_company` = {1, AAPL}. Staging has TSLA, 2026-09-27, close 250.00.
2. **Stub.** The pre-check finds TSLA missing and inserts it. The AUTOINCREMENT column assigns `company_key = 2`, name `Pending Profile Sync`.
3. **Fact load.** INNER JOIN matches TSLA to key 2. Nothing is dropped.
4. **Self-healing.** When FMP's TSLA profile arrives, the `dim_company` SCD1 MERGE matches on `symbol`, keeps key 2 and overwrites the placeholder with the real name. The fact table is never touched.

**Lesson.** A query that runs without error can still lose data. Make referential integrity a guarantee of the load order, not a hope.

## 2. Docker-in-Docker on Debian Trixie

The default docker-in-docker devcontainer feature fails on the Trixie base image. **Fix:** docker-outside-of-docker with `moby: false`.

## 3. Windows PowerShell vs. bash commands

Bash heredocs (`cat > file <<EOF`), `mkdir -p` and `cp` do not work in PowerShell. **Fix:** use `New-Item`, `Copy-Item` and .NET file writes, or run the setup from Codespaces (Linux).
