from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


NOTEBOOK_DIRECTORY = "/home/jhu/notebooks"
OUTPUT_DIRECTORY = "/home/jhu/notebooks/executed"


default_args = {
    "owner": "housing_pipeline_team",
    "depends_on_past": False,
    "retries": 0,
}


with DAG(
    dag_id="housing_cost_mental_health_pipeline",
    description=(
        "Extracts CDC, FRED/FHFA, and HUD data and loads the "
        "normalized housing and mental-health database."
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["housing", "mental-health", "data-engineering"],
) as dag:

    create_output_directory = BashOperator(
        task_id="create_output_directory",
        bash_command=f"mkdir -p {OUTPUT_DIRECTORY}",
    )

    extract_cdc_places = BashOperator(
        task_id="extract_cdc_places",
        bash_command=(
            f"papermill "
            f"{NOTEBOOK_DIRECTORY}/01_extract_cdc_places.ipynb "
            f"{OUTPUT_DIRECTORY}/01_extract_cdc_places_output.ipynb"
        ),
    )

    extract_fred_housing = BashOperator(
        task_id="extract_fred_housing",
        bash_command=(
            f"papermill "
            f"{NOTEBOOK_DIRECTORY}/02_extract_fred.ipynb "
            f"{OUTPUT_DIRECTORY}/02_extract_fred_output.ipynb"
        ),
    )

    extract_hud_homelessness = BashOperator(
        task_id="extract_hud_homelessness",
        bash_command=(
            f"papermill "
            f"{NOTEBOOK_DIRECTORY}/03_extract_HUD.ipynb "
            f"{OUTPUT_DIRECTORY}/03_extract_HUD_output.ipynb"
        ),
    )

    join_and_load_data = BashOperator(
        task_id="join_and_load_data",
        bash_command=(
            f"papermill "
            f"{NOTEBOOK_DIRECTORY}/04_join_data.ipynb "
            f"{OUTPUT_DIRECTORY}/04_join_data_output.ipynb"
        ),
    )

    (
        create_output_directory
        >> extract_cdc_places
        >> extract_fred_housing
        >> extract_hud_homelessness
        >> join_and_load_data
    )