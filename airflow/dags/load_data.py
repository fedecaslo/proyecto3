from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import os
from sqlalchemy import create_engine
import datetime as dt

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

def ganancias_por_dia():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    data = pd.read_sql(query, engine)
    data['tsO'] = pd.to_datetime(data['tsO'])
    data['tsD'] = pd.to_datetime(data['tsD'])
    # Hacer consulta aqui
    data['dia_inicio'] = data['tsO'].dt.date
    # Ganancias de viajes por día 
    viajes_por_dia = data.groupby('dia_inicio')['price'].sum()
    df = pd.DataFrame(viajes_por_dia).reset_index()

    # Guardar el resultado en una nueva tabla
    df.to_sql('ganancias_por_dia', engine, index=False, if_exists='replace')

def numero_viajes_por_patinete():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    data = pd.read_sql(query, engine)
    data['tsO'] = pd.to_datetime(data['tsO'])
    data['tsD'] = pd.to_datetime(data['tsD'])

    # Hacer consulta aqui
    df = data.idS.value_counts().reset_index()
    df.columns = ['idS', 'count']

    # Guardar el resultado en una nueva tabla
    df.to_sql('numero_viajes_por_patinete', engine, index=False, if_exists='replace')

def demanda_por_horas():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    data = pd.read_sql(query, engine)
    data['tsO'] = pd.to_datetime(data['tsO'])
    data['tsD'] = pd.to_datetime(data['tsD'])
    
    # Hacer consulta aqui
    data['dia'] = data['tsO'].dt.date
    data['hora'] = data.tsO.dt.hour
    df = data.groupby(['dia', 'hora']).size().reset_index(name='num_patinetes_demandados')

    # Guardar el resultado en una nueva tabla
    df.to_sql('demanda_por_horas', engine, index=False, if_exists='replace')

def resumen_diario_patinete():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    data = pd.read_sql(query, engine)
    data['tsO'] = pd.to_datetime(data['tsO'])
    data['tsD'] = pd.to_datetime(data['tsD'])
    
    # Hacer consulta aqui
    dist_max = data.groupby('idS')['dis'].max()
    dist_min = data.groupby('idS')['dis'].min()
    dist_media = data.groupby('idS')['dis'].mean()

    tiempo_max = data.groupby('idS')['tt'].max()
    tiempo_min = data.groupby('idS')['tt'].min()
    tiempo_medio = data.groupby('idS')['tt'].mean()

    velocidad_media = data.groupby('idS')['vel'].mean()

    data['consumo'] = data.dis * 13.5 / 1000
    viaje_mayor_consumo = data.groupby('idS')['consumo'].max()
    viaje_menor_consumo = data.groupby('idS')['consumo'].min()
    consumo_medio = data.groupby('idS')['consumo'].mean()
    consumo_total = data.groupby('idS')['consumo'].sum()

    ganancias_totales = data.groupby('idS')['price'].sum()
    df = pd.DataFrame({
        'dist_max': dist_max,
        'dist_min': dist_min,
        'dist_media': dist_media,
        'tiempo_max': tiempo_max,
        'tiempo_min': tiempo_min,
        'tiempo_medio': tiempo_medio,
        'velocidad_media': velocidad_media,
        'viaje_mayor_consumo': viaje_mayor_consumo,
        'viaje_menor_consumo': viaje_menor_consumo,
        'consumo_medio': consumo_medio,
        'consumo_total': consumo_total,
        'ganancias_totales': ganancias_totales
    }).reset_index()

    # Guardar el resultado en una nueva tabla
    df.to_sql('resumen_diario', engine, index=False, if_exists='replace')

def bateria_patinete():
    # Crear una conexión a PostgreSQL usando SQLAlchemy
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Realizar consulta SQL para obtener el número total de pacientes
    query = "SELECT * FROM rome_table"
    data = pd.read_sql(query, engine)
    data['tsO'] = pd.to_datetime(data['tsO'])
    data['tsD'] = pd.to_datetime(data['tsD'])
    
    # Hacer consulta aqui
    df_consumo = data.copy()
    dia_ultimo = df_consumo['tsO'].dt.date.max()
    df_consumo[df_consumo.tsD.dt.date == dia_ultimo]
    df_consumo['consumo'] = df_consumo['dis'] * 13.5 / 1000 # consumo constante de 13.5 Wh/km
    df_consumo = df_consumo.sort_values(by='tsO').reset_index(drop=True)
    df_consumo['bateria_restante'] = 576

    bateria_patinete = {}

    for idS in df_consumo.idS.unique():
        df_patinete = df_consumo[df_consumo['idS'] == idS].reset_index(drop=True)
        suma = df_patinete.consumo.sum()
        bateria_restante = max(0, round(((576 - suma) / 576 * 100), 2))
        bateria_patinete[idS] = bateria_restante

    bateria_patinete = pd.DataFrame(list(bateria_patinete.items()), columns=['idS', 'bateria_restante'])

    # Guardar el resultado en una nueva tabla
    bateria_patinete.to_sql('bateria_patinete', engine, index=False, if_exists='replace')

with dag:
    start_task = DummyOperator(task_id='start')

    cargar_csv_task = PythonOperator(
        task_id='cargar_csv_a_postgres',
        python_callable=cargar_csv_a_postgres
    )

    ganancias_por_dia_task = PythonOperator(
        task_id='ganancias_por_dia',
        python_callable=ganancias_por_dia
    )

    numero_viajes_por_patinete_task = PythonOperator(
        task_id='numero_viajes_por_patinete',
        python_callable=numero_viajes_por_patinete
    )

    demanda_por_horas_task = PythonOperator(
        task_id='demanda_por_horas',
        python_callable=demanda_por_horas
    )

    resumen_diario_patinete_task = PythonOperator(
        task_id='resumen_diario_patinete',
        python_callable=resumen_diario_patinete
    )

    bateria_patinete_task = PythonOperator(
        task_id='bateria_patinete',
        python_callable=bateria_patinete
    )

    end_task = DummyOperator(task_id='end')

    start_task >> cargar_csv_task >> ganancias_por_dia_task >> numero_viajes_por_patinete_task >> demanda_por_horas_task >> resumen_diario_patinete_task >> bateria_patinete_task >> end_task

