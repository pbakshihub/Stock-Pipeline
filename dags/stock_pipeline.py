from datetime import datetime, timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="stock_pipeline",
    start_date=datetime(2026, 9, 1),
    schedule="*/30 * * * *",   # every 30 minutes
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
    tags=["stocks"],
)
def stock_pipeline():
    @task
    def fetch_quotes() -> str:
        from include.fetch_quote import fetch_and_save
        return fetch_and_save()

    @task
    def load_to_db(filepath: str):
        from include.load_to_db import load_json_files
        load_json_files()

    load_to_db(fetch_quotes())


stock_pipeline()