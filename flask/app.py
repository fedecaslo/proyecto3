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
        filename = secure_filename(file.filename)
        file_path = os.path.abspath(os.path.join('csvs_for_upload', filename))
        os.makedirs('./csvs_for_upload', exist_ok=True)
        subprocess.run(['chmod', '755', './csvs_for_upload'])
        file.save(file_path)
        
        try:
            print(f'File "{filename}" uploaded to Flask')
            send_to_kafka(file_path)
            return 'File uploaded and sent to Kafka'
        except Exception as e:
            return f'Error: {str(e)}'
        finally:
            os.remove(file_path)
    else:
        return 'Invalid file type'

def send_to_kafka(filename):
    producer = Producer({'bootstrap.servers': 'kafka:9092'})
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            producer.produce('csv_upload', ','.join(row))
    producer.flush()
    os.remove(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
