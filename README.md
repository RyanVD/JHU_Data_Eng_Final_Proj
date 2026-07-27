# Housing Cost & Mental Health Pipeline

Examines whether declining housing affordability is associated with worse
mental health/sleep outcomes and rising homelessness at the U.S. county
level. Integrates three federal sources into a normalized Postgres schema:

- **CDC PLACES** — county-level mental health & sleep outcomes (CSV)
- **FRED / FHFA** — housing costs: national mortgage rate & rent (live FRED
  API), county-level House Price Index (bulk FHFA annual file)
- **HUD Point-in-Time** — homelessness counts by Continuum of Care (CSV),
  joined to counties via a population-weighted crosswalk

See `shared/Datasets Check-In_ Housing Cost & Mental Health Pipeline (1).docx`
for the full dataset writeup (join columns, field descriptions, sample data).

## Stack

- **Database:** PostgreSQL 16
- **Orchestration + notebooks + API:** one container (`airflow-jupyter`) running
  Apache Airflow 2.9.3 (webserver + scheduler), JupyterLab, and Flask together
- **DB browser:** pgAdmin4
- Everything runs via Docker Compose — no local Python/Postgres install needed.

## Project structure

```
.
├── .env.example           # copy to .env, fill in FRED_API_KEY
├── Dockerfile              # airflow-jupyter image (Airflow + Jupyter + pipeline deps)
├── docker-compose.yml      # postgres, pgadmin, airflow-jupyter services
├── db/
│   └── init/                # CREATE TABLE scripts, run automatically on first Postgres start
│       ├── 01_dimensions.sql
│       ├── 02_bridge.sql
│       └── 03_facts.sql
├── notebooks/               # extraction / transform notebooks (see below)
└── shared/                  # raw source CSVs, bind-mounted into the container at /home/jhu
```

## Setup

**Requires:** Docker Desktop only.

1. Copy the env file and add yours or my api key from whatsapp
   cp .env.example .env
   then edit .env and set FRED_API_KEY=
   ```
2. Build and start everything:
   ```bash
   docker compose up -d --build
   ```
   First build takes a few minutes (installs Airflow). Check it's healthy:
   ```bash
   docker compose ps
   ```
3. Local host access:
   - **JupyterLab:** http://localhost:8888 (no login token)
   - **Airflow UI:** http://localhost:8080 (admin/admin)
   - **Flask API:** http://localhost:5000 (not built yet — see Status below)
   - **pgAdmin:** http://localhost:8085 (`student@jhu.edu` / `password123`) —
     register a server manually: host `postgres`, port `5432`, user `jhu`,
     password `jhu123`, db `jhu`. This registration isn't persisted across a
     `docker compose down -v`, so you'll need to re-add it if you ever run
     that.

## Database schema

7 tables, star-schema style — see `db/init/*.sql` for full definitions:

- **Dimensions:** `Dim_County`, `Dim_Year`, `Dim_CoC`
- **Bridge:** `Bridge_CoC_County` — resolves the CoC-to-county many-to-many
  relationship (HUD reports by CoC, not county)
- **Facts:** `Fact_Mental_Health`, `Fact_Housing` (mixes county-level HPI with
  broadcast national mortgage/rent values — see `rate_geography_level`),
  `Fact_Homelessness`

## Pipeline notebooks

Run in this order — `01`-`03` each stage a `*_raw` table in Postgres; nothing
writes to the final `Dim_*`/`Fact_*` tables until `04_join_data.ipynb`.

| Notebook | Status | Populates |
|---|---|---|
| `01_extract_cdc_places.ipynb` | done | `cdc_places_raw` |
| `02_extract_fred.ipynb` | done | `fred_housing_raw` |
| `03_extract_HUD.ipynb` | done | `hud_pit_raw`, `bridge_coc_county_raw` |
| `04_join_data.ipynb` | done | `Dim_*` / `Fact_*` tables |

**01 must run before 02** — CDC PLACES is what populates the county list
(`Dim_County`) that FRED's county-level HPI eventually joins against at the
transform step. `04_join_data.ipynb` truncates and reloads all `Dim_*`/`Fact_*`
tables each time it runs, so it's safe to re-run after re-running `01`-`03`.

## recorded errors

- **`pandas` must stay pinned to `2.1.4`** in the Dockerfile. Airflow 2.9.3
  hard-pins `SQLAlchemy==1.4.52`; pandas 2.2+ dropped full support for
  SQLAlchemy <2.0 and silently breaks `to_sql`/`read_sql` with
  `AttributeError: 'Engine' object has no attribute 'cursor'` if you bump it.

## Status / what's left
TODO — next up

Airflow DAG 
Flask API (app.py) — at least one aggregated-report endpoint querying the Fact
Final documentation 

# Project Status

## Completed Features

- Designed and implemented a PostgreSQL star-schema database with three dimension tables, one bridge table, and three fact tables.
- Built automated extraction pipelines for CDC PLACES, FRED/FHFA housing data, and HUD Point-in-Time homelessness data.
- Developed a data transformation notebook that cleans, joins, and loads all datasets into the final database schema.
- Created an Apache Airflow DAG that executes the complete ETL pipeline using Papermill.
- Developed a Flask REST API that connects to PostgreSQL and provides aggregated reporting endpoints.
- Containerized the entire project using Docker Compose, including PostgreSQL, pgAdmin, Airflow, JupyterLab, and the Flask application.
- Designed and documented the project's Entity Relationship Diagram (ERD).

---

# API Endpoints

## GET /health

Verifies that the Flask application can successfully connect to the PostgreSQL database.

Example response:

```json
{
  "database": "connected",
  "status": "healthy"
}
```

---

## GET /api/state-summary

Returns aggregated housing, mental health, sleep, and homelessness statistics by state and year.

### Optional Parameters

| Parameter | Description |
|-----------|-------------|
| state | Two-letter state abbreviation (ex. TX) |
| year | Four-digit year (ex. 2023) |

Example request:

```
/api/state-summary?state=TX&year=2023
```

Example response:

```json
{
  "data": [
    {
      "average_housing_price_index": 429.97,
      "average_poor_mental_health_pct": 17.41,
      "average_poor_sleep_pct": null,
      "average_rent": 399.64,
      "county_count": 253,
      "estimated_homeless_count": 27325.11,
      "mortgage_rate_30yr": 6.81,
      "state": "TX",
      "year": 2023
    }
  ],
  "filters": {
    "state": "TX",
    "year": 2023
  },
  "result_count": 1
}
```

---

# Airflow Workflow

The ETL pipeline is orchestrated through the `housing_cost_mental_health_pipeline` DAG.

Execution order:

```
create_output_directory
        ↓
extract_cdc_places
        ↓
extract_fred_housing
        ↓
extract_hud_homelessness
        ↓
join_and_load_data
```

Each notebook executes sequentially using Papermill. The final notebook transforms the extracted datasets and reloads the dimension, bridge, and fact tables into PostgreSQL.

---

# Data Notes

- CDC PLACES provides different health indicators depending on the reporting year. As a result, some state-year combinations contain `null` values for either the poor mental health or poor sleep measure.
- HUD homelessness data is reported at the Continuum of Care (CoC) level. County estimates are calculated using the `Bridge_CoC_County` overlap ratios before being aggregated to the state level.
- Mortgage rates and rent values come from national-level datasets and are included to provide economic context alongside county-level housing and mental health data.
