from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic
import pandas as pd
import csv

# Configura las variables según tus configuraciones
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'csv_upload'


admin = AdminClient({'bootstrap.servers': 'kafka:9092'})
admin.create_topics([NewTopic(KAFKA_TOPIC)])


def send_to_kafka(filename):

    producer = Producer({'bootstrap.servers': 'kafka:9092'})
    metadata = producer.list_topics()
    print(f"Topics: {','.join(metadata.topics.keys())}")
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        from itertools import islice
        for row in islice(reader, 3):
            print("Row: ", row)
            producer.produce('csv_upload', ','.join(row))
    producer.flush()
    print("TODO ENVIADO")


send_to_kafka("data/prueba.csv")
