from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from sqlalchemy import create_engine
from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic
import pandas as pd
import csv
import os

# Configura las variables según tus configuraciones
# Configura las variables según tus configuraciones
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'csv_upload'

admin = AdminClient({'bootstrap.servers': 'kafka:9092'})
admin.create_topics([NewTopic(KAFKA_TOPIC)])
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
    catchup=False,  # Evitar la ejecución de tareas para ejecuciones anteriores no ejecutadas
)

def consume_kafka_and_save_to_csv(**kwargs):
    conf = {'bootstrap.servers': KAFKA_BROKER,
            'group.id':'default',
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest',
            'enable.auto.offset.store': True}
    consumer = Consumer(conf)

    try:
        consumer.subscribe([KAFKA_TOPIC])

        messages = []
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < 20:
            print(f"Esperando mensajes. Total leidos: {len(messages)}")
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    print("Error", msg.error())
                    continue
                else:
                    print(msg.error())
                    break

            messages.append(msg.value().decode('utf-8'))

    finally:
        consumer.close()

    output_dir = './kafka_data'
    os.makedirs(output_dir, exist_ok=True)

    # Puedes procesar los mensajes según tu lógica
    # Puedes procesar los mensajes según tu lógica
    header = messages[0]
    data = messages[1:]

    # Guarda el CSV con el encabezado y los datos
    with open(os.path.join(output_dir, 'data.csv'), 'w') as file:
        file.write(header + '\n')
        for message in data:
            file.write(message + '\n')

    return './kafka_data/data.csv'

def insert_csv_to_postgres():
    output_dir = './kafka_data'
    csv_path = os.path.join(output_dir, 'data.csv')

    engine = create_engine(POSTGRES_CONNECTION_STRING)
    df = pd.read_csv(csv_path)

    # Ajusta el nombre de la tabla según tus necesidades
    df.to_sql('rome_table', engine, index=False, if_exists='append')

with dag:
    start_task = DummyOperator(task_id='start')
    consume_task = PythonOperator(
        task_id='consume_kafka',
        python_callable=consume_kafka_and_save_to_csv,
    )

    insert_task = PythonOperator(
        task_id='insert_to_postgres',
        python_callable=insert_csv_to_postgres,
    )
    end_task = DummyOperator(task_id='end')
    start_task>>consume_task >> insert_task>>end_task
