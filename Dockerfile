FROM python:3.11-slim

WORKDIR /home/jhu

ENV AIRFLOW_VERSION=2.9.3
ENV PYTHON_VERSION=3.11

# Airflow needs its install pinned against a constraints file matched to
# both its own version and the Python version, otherwise pip's normal
# resolver can pull in incompatible sub-dependency versions.
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Everything else the notebooks / DAG / API will need.
# Flask itself is already pulled in as an Airflow dependency (via
# flask-appbuilder) — don't add it separately or pip may try to
# reconcile two different pinned versions.
RUN pip install --no-cache-dir \
    jupyterlab \
    papermill \
    "pandas==2.1.4" \
    sqlalchemy \
    psycopg2-binary \
    requests \
    openpyxl

EXPOSE 8888 8080 5000