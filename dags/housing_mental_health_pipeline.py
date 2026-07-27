from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "data_engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}


with DAG(
    dag_id="housing_mental_health_pipeline",
    description="Extracts, transforms, and loads the project datasets",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["data-engineering", "final-project"]
) as dag:

    extract_cdc = BashOperator(
        task_id="extract_cdc_places",
        bash_command="""
        mkdir -p /tmp/pipeline_runs
        papermill \
            /home/jhu/notebooks/01_extract_cdc_places.ipynb \
            /tmp/pipeline_runs/01_extract_cdc_places.ipynb
        """
    )

    extract_fred = BashOperator(
        task_id="extract_fred_housing",
        bash_command="""
        mkdir -p /tmp/pipeline_runs
        papermill \
            /home/jhu/notebooks/02_extract_fred.ipynb \
            /tmp/pipeline_runs/02_extract_fred.ipynb
        """
    )

    extract_hud = BashOperator(
        task_id="extract_hud_homelessness",
        bash_command="""
        mkdir -p /tmp/pipeline_runs
        papermill \
            /home/jhu/notebooks/03_extract_HUD.ipynb \
            /tmp/pipeline_runs/03_extract_HUD.ipynb
        """
    )

    join_and_load = BashOperator(
        task_id="join_and_load_final_tables",
        bash_command="""
        mkdir -p /tmp/pipeline_runs
        papermill \
            /home/jhu/notebooks/04_join_data.ipynb \
            /tmp/pipeline_runs/04_join_data.ipynb
        """
    )

    extract_cdc >> extract_fred >> extract_hud >> join_and_load