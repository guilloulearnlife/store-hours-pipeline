from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="store_hours_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
) as dag:

    scrape = BashOperator(
        task_id="scrape",
        bash_command="npm run scrape",
        cwd="/opt/projects/store-hours-pipeline"
    )

    process = BashOperator(
        task_id="process",
        bash_command="npm run process",
        cwd="/opt/projects/store-hours-pipeline"
    )

    index = BashOperator(
        task_id="index",
        bash_command="npm run index",
        cwd="/opt/projects/store-hours-pipeline"
    )

    scrape >> process >> index
