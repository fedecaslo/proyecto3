from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from confluent_kafka import Producer
import csv
import os
import subprocess

app = Flask(__name__, template_folder='./plantillas')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
    if file and file.filename.endswith('.csv'):
        os.makedirs('./csvs_for_upload', exist_ok=True)
        file.save('./csvs_for_upload/'+ file.filename)

        try:
            print(f'File "{file.filename}" uploaded to Flask')
            send_to_kafka('./csvs_for_upload/'+ file.filename)
            return 'File uploaded and sent to Kafka'
        except Exception as e:
            return f'Error: {str(e)}'
    else:
        return 'Invalid file type'

def send_to_kafka(filename):
    producer = Producer({'bootstrap.servers': 'kafka:9092'})
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            producer.produce('csv_upload', ','.join(row))
    producer.flush()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
