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
        for row in islice(reader, 20):
            print("Row: ", row)
            producer.produce('csv_upload', ','.join(row))
    producer.flush()
    print("TODO ENVIADO")



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
        while True:
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

    # Puedes procesar los mensajes según tu lógica
    df = pd.DataFrame(messages)
    df.to_csv('./kafka_data/data.csv', index=False)

    return './kafka_data/data.csv'


send_to_kafka("data/rome_u_journeys.csv")
consume_kafka_and_save_to_csv()