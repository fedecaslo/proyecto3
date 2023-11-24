from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

# Define la conexión a PostgreSQL
POSTGRES_CONN_ID = 'postgres:5432'  # Reemplaza con el nombre de tu conexión
POSTGRES_TABLE_NAME = 'rome_table'

# Ruta del archivo CSV
CSV_FILE_PATH = './data/rome_u_journeys.csv'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'cargar_csv_a_postgres',
    default_args=default_args,
    description='Un DAG simple para cargar un archivo CSV en PostgreSQL',
    schedule_interval='@daily',  # Puedes ajustar la frecuencia según tus necesidades
)

def cargar_csv_a_postgres():
    # Cargar el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(CSV_FILE_PATH)

    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine(f'postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}')

    # Cargar el DataFrame en la base de datos
    df.to_sql(POSTGRES_TABLE_NAME, engine, index=False, if_exists='replace')

with dag:
    start_task = DummyOperator(task_id='start')

    cargar_csv_task = PythonOperator(
        task_id='cargar_csv_a_postgres',
        python_callable=cargar_csv_a_postgres
    )

    end_task = DummyOperator(task_id='end')

    start_task >> cargar_csv_task >> end_task