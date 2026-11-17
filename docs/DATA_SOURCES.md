# Data Sources and Raw Schemas

> Bronze scope: **nothing is filtered**. Everything below lands untouched in the landing zone and Bronze.

## How they relate

| | Twelve Data | FMP |
|---|---|---|
| Kind | Time-series market data | Descriptive reference data |
| Speed | Fast-moving, numeric, new record per ticker per day | Slow-moving, mostly static |
| Warehouse role | **Fact** | **Dimension** |

They join on the ticker `symbol`. Neither alone answers a useful business question: prices lack context, profiles lack performance.

## Twelve Data: `GET /time_series`

```text
https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize={n}&apikey={key}
```

| Field | Type | Notes |
|---|---|---|
| meta.symbol | string | Ticker |
| meta.interval | string | e.g. "1day" |
| meta.currency | string | |
| meta.exchange_timezone | string | |
| meta.exchange | string | e.g. "NASDAQ" |
| meta.mic_code | string | e.g. "XNGS" |
| meta.type | string | e.g. "Common Stock" |
| values[].datetime | string (date) | Trading date |
| values[].open / high / low / close / volume | string (numeric) | |
| status | string | "ok" on success |

## FMP: `GET /stable/profile`

```text
https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={key}
```

35 fields: symbol, price, marketCap, beta, lastDividend, range, change, changePercentage, volume, averageVolume, companyName, currency, cik, isin, cusip, exchangeFullName, exchange, industry, website, description, ceo, sector, country, fullTimeEmployees, phone, address, city, state, zip, image, ipoDate, defaultImage, isEtf, isActivelyTrading, isAdr, isFund.

Silver keeps 12 of them: see [ADR 4](DECISIONS.md#adr-4).

## Business questions

- **Performance comparison**: best/worst return over the last 30 days
- **Sector-relative performance**: is a move typical for the sector or an outlier?
- **Volatility ranking**: widest daily high-low spread as a risk indicator
- **Volume anomalies**: unusually high volume vs. a company's own average
- **Exchange breakdown**: NASDAQ vs. other exchanges
- **Trend visualization**: candlestick / line charts, filterable by sector or company
- **IPO-age vs volatility**: do newer listings swing more?

These exercise real window functions (moving averages, day-over-day %, rank within sector), not just GROUP BY.
