from flask import Flask, request
from werkzeug.utils import secure_filename
from confluent_kafka import Producer
import csv
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file.save(filename)
        send_to_kafka(filename)
        return 'File uploaded and sent to Kafka'
    else:
        return 'Invalid file type'

def send_to_kafka(filename):
    producer = Producer({'bootstrap.servers': 'localhost:9092'})
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            producer.produce('mytopic', ','.join(row))
    producer.flush()
    os.remove(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)