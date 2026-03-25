# airflow/dags/rent_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.expanduser('~/ireland-rent-tracker'))

default_args = {
    'owner': 'rohit',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
    'depends_on_past': False,
}

def scrape_rtb_data():
    print("🚀 Task 1: Scraping RTB data...")
    from scraper.rtb_scraper import (
        extract_rtb_data,
        transform_rtb_data,
        load_to_s3
    )
    RTB_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIA02/CSV/1.0/en"
    S3_BUCKET = os.getenv("S3_BUCKET", "ireland-rent-tracker-raw-data")
    S3_PREFIX = "raw/rtb/"

    raw_df   = extract_rtb_data(RTB_URL)
    clean_df = transform_rtb_data(raw_df)
    s3_key   = load_to_s3(clean_df, S3_BUCKET, S3_PREFIX)
    print(f"✅ Task 1 complete — {s3_key}")
    return s3_key

def load_to_redshift():
    print("🚀 Task 2: Loading to Redshift...")
    from sql.load_data import (
        get_connection,
        get_iam_role_arn,
        get_latest_s3_file,
        truncate_raw_table,
        load_s3_to_redshift,
        verify_load
    )
    iam_role = get_iam_role_arn()
    s3_path  = get_latest_s3_file()
    conn     = get_connection()
    conn.autocommit = True
    cursor   = conn.cursor()

    truncate_raw_table(cursor)
    load_s3_to_redshift(cursor, s3_path, iam_role)
    verify_load(cursor)

    cursor.close()
    conn.close()
    print("✅ Task 2 complete")

with DAG(
    dag_id='ireland_rent_pipeline',
    default_args=default_args,
    description='Daily pipeline — RTB → S3 → Redshift → dbt',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ireland', 'rent', 'rtb'],
) as dag:

    task_scrape = PythonOperator(
        task_id='scrape_rtb_data',
        python_callable=scrape_rtb_data,
    )

    task_load = PythonOperator(
        task_id='load_to_redshift',
        python_callable=load_to_redshift,
    )

    task_dbt = BashOperator(
        task_id='run_dbt_models',
        bash_command=f'cd {os.path.expanduser("~")}/ireland-rent-tracker/dbt && dbt run',
    )

    task_scrape >> task_load >> task_dbt