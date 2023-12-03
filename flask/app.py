from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from confluent_kafka import Producer
import csv
import os
import subprocess
from google.cloud import dialogflow_v2beta1 as dialogflow
import json
import pusher

app = Flask(__name__, template_folder='./plantillas')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    print(req)

    return{
        'fulfillmentText':'Hello from the other side Lu' 
    }

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.Sessiogit nsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)


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
