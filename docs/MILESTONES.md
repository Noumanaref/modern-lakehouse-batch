# Roadmap

Tick boxes as milestones complete.

- [ ] **1. Environment setup**: repo, Codespace, Docker Compose, Terraform buckets, Snowflake account
- [ ] **2. Ingestion**: `canonical_hash.py`, `twelvedata_ingest.py`, `fmp_ingest.py`. Checkpoint: second run writes zero new files. First step: diff two real responses to build `EXCLUDE_KEYS`.
- [ ] **3. Orchestration**: Airflow DAG `[ingest x2] -> transform -> load -> quality -> alert`
- [ ] **4. Processing**: Autoloader Bronze + PySpark Silver. Checkpoint: zero new rows on rerun; `versionAsOf` time travel works.
- [ ] **5. Warehouse**: DDL, external stage, high-water mark, MERGE loads, weekly reconciliation
- [ ] **6. Data quality**: Great Expectations gates that halt the pipeline
- [ ] **7. CI/CD**: `ci.yml`, `deploy.yml`, branch protection, rollback doc
- [ ] **8. Monitoring**: Slack alerts distinguishing "pipeline failed" from "quality check failed"
- [ ] **9. Docs and polish**: runbook, data dictionary, README screenshots, demo

Milestone 3 is built incrementally alongside 2, 4 and 5; Milestone 6 is integrated into 2, 4 and 5.
