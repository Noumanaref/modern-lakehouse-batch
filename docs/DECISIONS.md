# Architecture Decision Records

| ADR | Title | Status |
|---|---|---|
| [1](#adr-1) | Content-hash filenames for ingestion idempotency | Accepted |
| [2](#adr-2) | Hybrid Snowflake load strategy | Accepted |
| [3](#adr-3) | Twelve Data + FMP as sources | Accepted |
| [4](#adr-4) | Filter only at Silver (Option A) | Accepted |
| [5](#adr-5) | Codespace + Docker Compose, no external VM | Accepted |
| [6](#adr-6) | Auto-stub for early-arriving facts | Accepted |
| [7](#adr-7) | Autoloader with availableNow and per-source checkpoints | Accepted |
| [8](#adr-8) | Layered idempotency | Accepted |
| [9](#adr-9) | docker-outside-of-docker in the devcontainer | Accepted |

---

<a id="adr-1"></a>
## ADR 1: Content-hash filenames for ingestion idempotency

**Context.** Autoloader's checkpoint tracks file *paths*. Overwriting a path with new content makes Autoloader silently skip it (stale data, no error). Timestamp/UUID names fix that but make every rerun, even of identical data, produce a new file and waste Bronze compute.

**Decision.** One immutable landing zone. Filename = sha256 of the canonicalized payload. The *original, untouched* payload is what is stored.

1. Parse the API response
2. Canonicalize: strip noise/envelope keys (`EXCLUDE_KEYS`), sort keys, minimal separators
3. sha256 the canonical form -> filename
4. Write the original payload under that name

**Consequences.**
- Identical content -> identical key -> the S3 PUT is a no-op. Changed content -> new key.
- Content-addressable storage, the same pattern as Git, Docker layers and IPFS. The uniqueness check is an O(1) key lookup done by S3.
- SHA-256 is never the bottleneck; network I/O and API rate limits are.
- **Validation required** before locking `EXCLUDE_KEYS`: diff two real responses made minutes apart and exclude only fields observed to change. Never guess.

<a id="adr-2"></a>
## ADR 2: Hybrid Snowflake load strategy

| Table | Strategy | Why |
|---|---|---|
| `dim_company` | Incremental MERGE (SCD Type 1) on `symbol` | Attributes change rarely; avoids reloading the dimension daily |
| `dim_date` | Static, built once | Calendar; never reloaded |
| `fact_stock_prices` | Incremental MERGE on `(company_key, date_key)` | Unbounded growth; idempotent reruns; flat compute |

Supporting mechanisms: high-water-mark control table (stage only new Silver partitions), `updated_at` stamping, weekly S3-vs-Snowflake reconciliation (row counts and checksums).

**Why not full refresh everywhere:** cost and runtime grow with the fact table. **Why not a single strategy:** one size does not fit bounded and unbounded tables.

<a id="adr-3"></a>
## ADR 3: Twelve Data + FMP as sources

**Decision.** Twelve Data (price) + Financial Modeling Prep (fundamentals), joined on `symbol`.

**Why.** The original PokeAPI + Weather.gov pair had no genuine shared key; any join would have been manufactured. `symbol` is a real natural key in both APIs and supports real questions (performance, volatility, sector comparison).

**Rejected.** Alpha Vantage: 25 req/day is too tight for a scheduled daily job with retry margin. Twelve Data (800/day) and FMP (250/day) leave headroom.

<a id="adr-4"></a>
## ADR 4: Filter only at Silver (Option A)

**Decision.** Nothing is dropped at ingestion or Bronze. Bronze is the insurance policy: if Silver filters wrongly, reprocess from a complete copy.

| Source | Kept | Dropped |
|---|---|---|
| FMP | symbol, companyName, sector, industry, exchange, exchangeFullName, country, currency, ipoDate, cik, isin, cusip | Live market fields (price, marketCap, beta, volume, averageVolume, change, changePercentage, range, lastDividend) because they duplicate Twelve Data and would break SCD Type 1; plus ceo, fullTimeEmployees, phone, address, city, state, zip, website, description, image, isEtf, isActivelyTrading, isAdr, isFund, defaultImage |
| Twelve Data | All fields | None |

<a id="adr-5"></a>
## ADR 5: Codespace + Docker Compose, no external VM

Same pattern as the Fraud Detection MLOps project. Airflow (Postgres + LocalExecutor, no Celery/Redis at this scale) and a Spark master + worker run in Compose. CI/CD uses GitHub Actions cloud runners. Secrets live only in Codespace / GitHub Secrets.

**Open item.** Whether the Codespace must stay up for unattended scheduled runs.

<a id="adr-6"></a>
## ADR 6: Auto-stub (inferred member) for early-arriving facts

**Problem.** A price row can arrive before its company profile exists in `dim_company`. See [PROBLEMS_FACED.md](PROBLEMS_FACED.md).

**Decision.** Before the fact MERGE, insert a real stub row (`'Pending Profile Sync'`) for every unknown symbol. The fact load can then safely INNER JOIN. When the real profile arrives, the SCD1 MERGE fills in the same row.

**Rejected.** INNER JOIN alone (silent data loss), `COALESCE(key, -1)` (orphans moved into BI), and a `-1 'Unresolved'` seed row (visible but never resolved).

<a id="adr-7"></a>
## ADR 7: Autoloader with `availableNow` and per-source checkpoints

- `trigger(availableNow=True)`: process everything new since the last checkpoint, then stop. Genuinely batch, still incremental.
- Directory-listing mode, RocksDB-backed checkpoint keyed on file path.
- One checkpoint per source (`bronze_twelvedata`, `bronze_fmp`): different schemas, independent failure and retry.

<a id="adr-8"></a>
## ADR 8: Layered idempotency

| Layer | Guarantee | Mechanism |
|---|---|---|
| Landing (S3) | No redundant files for identical data | Content-hash filename |
| Bronze | Each file ingested once | Autoloader checkpoint |
| Silver | No duplicate business records | Explicit dedup |
| Gold | One row per business event | MERGE on natural key |

Bronze is deliberately permissive (append-only). Exactly-once at the business level is enforced downstream where "duplicate" can be defined correctly.

<a id="adr-9"></a>
## ADR 9: docker-outside-of-docker in the devcontainer

The default docker-in-docker feature fails on the Debian Trixie base image. Use docker-outside-of-docker with `moby: false`.

## Open items

- SCD Type 2 for `dim_company` if "as-of" historical analytics are needed (revisit in Milestone 5).
- Always-on scheduler vs. a Codespace that must stay running.
- Terraform remote state (currently local, accepted for a single developer).
