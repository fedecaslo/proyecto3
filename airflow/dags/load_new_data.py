from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from confluent_kafka import Consumer, KafkaException
from sqlalchemy import create_engine

# Configura las variables según tus configuraciones
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'csv_upload'
POSTGRES_CONNECTION_STRING = 'postgresql://admin:admin@postgres:5432/rome'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kafka_to_postgres',
    default_args=default_args,
    schedule_interval=timedelta(minutes=30),  # Ajusta según tus necesidades
)

def consume_kafka_and_save_to_csv(**kwargs):
    conf = {'bootstrap.servers': KAFKA_BROKER, 'group.id':'fede'}
    consumer = Consumer(conf)

    try:
        consumer.subscribe([KAFKA_TOPIC])

        messages = []
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            messages.append(msg.value().decode('utf-8'))

    finally:
        consumer.close()

    # Puedes procesar los mensajes según tu lógica
    df = pd.DataFrame(messages)
    df.to_csv('./kafka_data/data.csv', index=False)

    return './kafka_data/data.csv'

def insert_csv_to_postgres(**kwargs):
    csv_path = kwargs['ti'].xcom_pull(task_ids='consume_kafka')['return_value']

    engine = create_engine(POSTGRES_CONNECTION_STRING)
    df = pd.read_csv(csv_path)

    # Ajusta el nombre de la tabla según tus necesidades
    df.to_sql('your_postgres_table', engine, index=False, if_exists='append')

with dag:
    consume_task = PythonOperator(
        task_id='consume_kafka',
        python_callable=consume_kafka_and_save_to_csv,
    )

    insert_task = PythonOperator(
        task_id='insert_to_postgres',
        python_callable=insert_csv_to_postgres,
    )

    consume_task >> insert_task
