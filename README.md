# World Cup dbt Practice Pipeline

A small end-to-end analytics engineering pipeline built from scratch:
football-data.org API → raw JSON landed in DuckDB → dbt staging and marts models,
tested and documented.

## Structure
- `scripts/ingest.py` — pulls match data from the API and lands it as raw JSON
- `notebooks/` — exploratory API testing (not part of the production pipeline)
- `wc_dbt_practice/` — the dbt project itself (staging + marts models, tests, docs)

## Running it
1. `source venv/bin/activate`
2. `python scripts/ingest.py`
3. `cd wc_dbt_practice && dbt build`