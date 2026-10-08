from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

BRONZE_JOB_ID = "1056327494372382"
SILVER_JOB_ID = "775942761957363"

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='market_lakehouse_batch',
    default_args=default_args,
    description='End-to-End Market Lakehouse Pipeline',
    schedule='0 2 * * 2-6',
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=['lakehouse', 'finance', 'batch'],
    template_searchpath=['/opt/airflow/project_root/sql/load']
) as dag:

    #  INGESTION LAYER
    
    ingest_twelvedata = BashOperator(
        task_id='ingest_twelvedata',
        bash_command='python /opt/airflow/project_root/ingestion/twelvedata_ingest.py'
    )

    ingest_fmp = BashOperator(
        task_id='ingest_fmp',
        bash_command='python /opt/airflow/project_root/ingestion/fmp_ingest.py'
    )

    #  DATABRICKS LAKEHOUSE LAYER
    
    bronze_twelvedata = DatabricksRunNowOperator(
        task_id='bronze_twelvedata',
        databricks_conn_id='databricks_default',
        job_id=BRONZE_JOB_ID,
        notebook_params={'data_source': 'twelvedata'}
    )

    bronze_fmp = DatabricksRunNowOperator(
        task_id='bronze_fmp',
        databricks_conn_id='databricks_default',
        job_id=BRONZE_JOB_ID,
        notebook_params={'data_source': 'fmp'}
    )

    silver = DatabricksRunNowOperator(
        task_id='databricks_silver_processing',
        databricks_conn_id='databricks_default',
        job_id=SILVER_JOB_ID
    )

    #  STAGING & FIREWALL LAYER
    
    refresh_staging = SQLExecuteQueryOperator(
        task_id='refresh_staging',
        conn_id='snowflake_default',
        sql='load_stg_tables.sql',
        split_statements=True
    )

    quality_checks = BashOperator(
        task_id='quality_checks',
        bash_command='cd /opt/airflow/project_root/tests && python run_quality_checks.py',
        retries=0
    )

    #  GOLD WAREHOUSE LAYER (Kimball Merges)
    
    load_dim_company = SQLExecuteQueryOperator(
        task_id='load_dim_company',
        conn_id='snowflake_default',
        sql='load_dim_company.sql',
        split_statements=True
    )

    load_fact_stock_prices = SQLExecuteQueryOperator(
        task_id='load_fact_stock_prices',
        conn_id='snowflake_default',
        sql='load_fact_stock_prices.sql',
        split_statements=True
    )

    
    # ORCHESTRATION GRAPH
    
    [ingest_twelvedata, ingest_fmp] >> bronze_twelvedata >> bronze_fmp >> silver >> refresh_staging
    
    refresh_staging >> quality_checks
    
    quality_checks >> load_dim_company >> load_fact_stock_prices