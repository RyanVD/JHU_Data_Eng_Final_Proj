import os

from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
