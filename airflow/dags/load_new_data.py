from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.kafka.operators.kafka import KafkaToPandasOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 28),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kafka_to_postgres',
    default_args=default_args,
    description='A DAG to read messages from Kafka and insert into a Postgres table',
    schedule_interval=timedelta(days=1),
)

def process_and_insert_data(**kwargs):
    # Read messages from Kafka into a Pandas DataFrame
    kafka_to_pandas = KafkaToPandasOperator(
        task_id='kafka_to_pandas_task',
        kafka_topic='csv_upload',
        bootstrap_servers='kafka:9092',
        value_deserializer=lambda x: pd.DataFrame(x),
        dag=dag,
    )
    
    # Process the data if needed
    processed_data = process_data(kafka_to_pandas.output)

    # Insert the processed data into the existing Postgres table
    insert_into_postgres = PostgresOperator(
        task_id='insert_into_postgres_task',
        sql="INSERT INTO your_table SELECT * FROM your_table UNION ALL SELECT * FROM %s",
        parameters=[processed_data],
        postgres_conn_id='postgresql://admin:admin@postgres:5432/rome',
        autocommit=True,
        dag=dag,
    )

kafka_to_postgres_task = PythonOperator(
    task_id='process_and_insert_data_task',
    python_callable=process_and_insert_data,
    provide_context=True,
    dag=dag,
)

kafka_to_pandas >> kafka_to_postgres_task