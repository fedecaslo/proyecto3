from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import os
from sqlalchemy import create_engine

# Define la conexión a PostgreSQL
POSTGRES_CONN_ID = 'postgres_conn_id'  # Reemplaza con el nombre de tu conexión
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
    description='Un DAG simple para cargar un archivo CSV en PostgreSQL y realizar consulta',
    schedule_interval='@daily',  # Puedes ajustar la frecuencia según tus necesidades
    catchup=False,  # Evitar la ejecución de tareas para ejecuciones anteriores no ejecutadas
)

def cargar_csv_a_postgres():
    # Log the CSV file path
    logging.info(f"Current working directory: {os.getcwd()}")

    # Cargar el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(CSV_FILE_PATH)

    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Cargar el DataFrame en la base de datos
    df.to_sql(POSTGRES_TABLE_NAME, engine, index=False, if_exists='replace')

def ganancias_por_día():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    df= pd.read_sql(query, engine)

    # Hacer consulta aqui

    # Guardar el resultado en una nueva tabla
    df.to_sql('ganancia_por_dia', engine, index=False, if_exists='replace')

with dag:
    start_task = DummyOperator(task_id='start')

    cargar_csv_task = PythonOperator(
        task_id='cargar_csv_a_postgres',
        python_callable=cargar_csv_a_postgres
    )

    consultar_pacientes_task = PythonOperator(
        task_id='consultar_total_pacientes',
        python_callable=consultar_total_patinetes
    )

    end_task = DummyOperator(task_id='end')

    start_task >> cargar_csv_task >> consultar_pacientes_task >> end_task

