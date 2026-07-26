import os
from decimal import Decimal

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text


app = Flask(__name__)

# Uses DB_URL when provided. Otherwise, it connects to the Postgres
# service configured in docker-compose.yml.
DB_URL = os.environ.get(
    "DB_URL",
    "postgresql://jhu:jhu123@postgres:5432/jhu"
)

engine = create_engine(DB_URL, pool_pre_ping=True)


@app.route("/")
def home():
    return jsonify({
        "message": "Housing Cost and Mental Health API",
        "endpoints": {
            "health": "/health",
            "state_summary": "/api/state-summary"
        }
    })


@app.route("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception as error:
        print(f"Database connection error: {error}")

        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 500

@app.route("/api/state-summary")
def state_summary():
    state = request.args.get("state")
    year = request.args.get("year")

    # Validate the state filter
    if state:
        state = state.upper()

        if len(state) != 2 or not state.isalpha():
            return jsonify({
                "error": "State must be a two-letter abbreviation, such as MD or CA."
            }), 400

    # Validate the year filter
    if year:
        try:
            year = int(year)
        except ValueError:
            return jsonify({
                "error": "Year must be a four digits number, such as 2023."
            }), 400

    conditions = []
    parameters = {}

    if state:
        conditions.append("c.state_abbr = :state")
        parameters["state"] = state

    if year:
        conditions.append("m.year = :year")
        parameters["year"] = year

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = text(f"""
        WITH county_homelessness AS (
            SELECT
                b.county_fips,
                h.year,
                SUM(
                    h.total_homeless_count * b.overlap_ratio
                ) AS estimated_homeless_count
            FROM bridge_coc_county b
            JOIN fact_homelessness h
                ON b.coc_code = h.coc_code
            GROUP BY b.county_fips, h.year
        )
        SELECT
            c.state_abbr AS state,
            m.year,
            COUNT(DISTINCT c.county_fips) AS county_count,
            ROUND(AVG(m.poor_mental_health_pct), 2)
                AS average_poor_mental_health_pct,
            ROUND(AVG(m.poor_sleep_pct), 2)
                AS average_poor_sleep_pct,
            ROUND(AVG(housing.housing_price_index), 2)
                AS average_housing_price_index,
            ROUND(AVG(housing.mortgage_rate_30yr), 2)
                AS mortgage_rate_30yr,
            ROUND(AVG(housing.average_rent), 2)
                AS average_rent,
            ROUND(SUM(homeless.estimated_homeless_count), 2)
                AS estimated_homeless_count
        FROM dim_county c
        JOIN fact_mental_health m
            ON c.county_fips = m.county_fips
        LEFT JOIN fact_housing housing
            ON c.county_fips = housing.county_fips
            AND m.year = housing.year
        LEFT JOIN county_homelessness homeless
            ON c.county_fips = homeless.county_fips
            AND m.year = homeless.year
        {where_clause}
        GROUP BY c.state_abbr, m.year
        ORDER BY c.state_abbr, m.year
    """)

    try:
        with engine.connect() as connection:
            rows = connection.execute(query, parameters).mappings().all()

        results = []

        for row in rows:
            clean_row = {}

            for column, value in row.items():
                if isinstance(value, Decimal):
                    clean_row[column] = float(value)
                else:
                    clean_row[column] = value

            results.append(clean_row)

        return jsonify({
            "filters": {
                "state": state,
                "year": year
            },
            "result_count": len(results),
            "data": results
        }), 200

    except Exception as error:
        print(f"State summary error: {error}")

        return jsonify({
            "error": "The state summary could not be generated."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
