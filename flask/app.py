from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from confluent_kafka import Producer
import csv
import os
import subprocess
from google.cloud import dialogflow_v2beta1 as dialogflow
import json
import pusher
from sqlalchemy import create_engine
import pandas as pd
import re
from datetime import datetime
from tabulate import tabulate

app = Flask(__name__, template_folder='./plantillas')
lista_elementos = ['(A)','(B)','(C)','(D)', '(E)']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/webhook', methods=['POST'])
def webhook(message):
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

def webhook(message):
    engine = create_engine('postgresql://admin:admin@postgres:5432/rome')  # Ajusta la cadena de conexión según tu configuración

    # Inicializa modified_message con el mensaje original
    modified_message = message

    if '(A)' in message:
        pattern = re.compile(r'([A-Z]\d[A-Z]\d)')
        match = pattern.search(message)
        query = f'SELECT count FROM numero_viajes_por_patinete WHERE numero_viajes_por_patinete."idS" = \'{match.group(1)}\''
        data = pd.read_sql(query, engine)
        if not data.empty:
            # Si hay datos en el resultado de la consulta
            count_value = data.iloc[0, 0]
            modified_message = message.replace('(A)', str(count_value))
        else:
            # Si no hay datos en la consulta, se informa que no hay viajes asociados
            modified_message = "No tenemos ningún viaje asociado al ID de ese patinete. ¿Quieres realizar otra consulta?"
    
    if '(B)' in message:
        pattern = re.compile(r'A(\d{4})M(\d{2})D(\d{2})')
        matches = pattern.findall(message)
        if len(matches) == 2:
            fecha1, fecha2 = matches[:2]  # Tomamos las dos primeras fechas encontradas
            fecha_str = '-'.join(fecha1)
            fecha_1 = datetime.strptime(fecha_str, '%Y-%m-%d')
            fecha_str2 = '-'.join(fecha2)
            fecha_2= datetime.strptime(fecha_str2, '%Y-%m-%d')
            query1 = f'SELECT price FROM ganancias_por_dia WHERE dia_inicio = \'{fecha_1}\''
            data1 = pd.read_sql(query1, engine)
            query2 = f'SELECT price FROM ganancias_por_dia WHERE dia_inicio = \'{fecha_2}\''
            data2 = pd.read_sql(query2, engine)
            if not data1.empty and not data2.empty:
                count_value1= data1.iloc[0, 0]
                count_value2= data2.iloc[0, 0]
                count_value = count_value1 - count_value2
                modified_message = f"La diferencia de ganancias entre {fecha_str} y {fecha_str2} es de {count_value} euros. Siendo las ganancias del {fecha_str} un total de {count_value1} euros y del {fecha_str2} {count_value2} euros "
            elif not data1.empty:
                count_value1 = data1.iloc[0, 0]
                modified_message = f"Para la fecha {fecha_str} tenemos registros de ingresos y fueron {count_value1}.No hay datos registrados para la fecha {fecha_str2}"
 
            elif not data2.empty:
                count_value2 = data2.iloc[0, 0]
                modified_message= f"Para la fecha {fecha_str2} tenemos registros de ingresos y fueron {count_value2}.No hay datos registrados para la fecha {fecha_str}"
 
            else:
                modified_message = f"No tenemos datos registrados para ninguna de las fechas: {fecha_str} y {fecha_str2}. ¿Quieres realizar otra consulta?"
    
    if '(C)' in message:
        pattern = re.compile(r'A(\d{4})M(\d{2})D(\d{2})')
        match = pattern.findall(message)
        fecha_str = '-'.join(match[0])
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        hora_pattern = re.compile(r'H(\d{1,2})')
        hora_match = hora_pattern.search(message)
        query = f'SELECT num_patinetes_demandados FROM demanda_por_horas WHERE dia = \'{fecha}\' and hora = {hora_match.group(1)}'
        data = pd.read_sql(query, engine)
        if not data.empty:
            count_value = data.iloc[0, 0]
            modified_message = f"El día {fecha_str} a las {hora_match.group(1)} se realizaron un total de {count_value} viajes."
        else:
            modified_message = f"No existe un registro de viajes asociado al dís {fecha_str} a las {hora_match.group(1)} horas. ¿Quieres realizar otra consulta?"

    if '(D)' in message:
        pattern = re.compile(r'([A-Z]\d[A-Z]\d)')
        match = pattern.search(message)
        query = f'SELECT * FROM resumen_diario WHERE "idS" = \'{match.group(1)}\''
        data = pd.read_sql(query, engine)
        
        if not data.empty:
            # Si hay datos en el resultado de la consulta
            count_value = "\n".join([f"\n- {column}: {value}\n" for column, value in data.iloc[0].items()])
            modified_message = f"Datos asociados al ID del patinete:\n{count_value}\n"
        else:
            # Si no hay datos en la consulta, se informa que no hay viajes asociados
            modified_message = "No tenemos ningún viaje asociado al ID de ese patinete. ¿Quieres realizar otra consulta?"

    if '(E)' in message:
        pattern = re.compile(r'([A-Z]\d[A-Z]\d)')
        match = pattern.search(message)
        query = f'SELECT bateria_restante FROM bateria_patinete WHERE "idS" = \'{match.group(1)}\''
        data = pd.read_sql(query, engine)
        
        if not data.empty:
            # Si hay datos en el resultado de la consulta
            count_value = data.iloc[0,0]
            modified_message = modified_message = message.replace('(E)', str(count_value))
        else:
            # Si no hay datos en la consulta, se informa que no hay viajes asociados
            modified_message = "No tenemos ningún viaje asociado al ID de ese patinete. ¿Quieres realizar otra consulta?"

    return modified_message


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
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
    if any(elemento in fulfillment_text for elemento in lista_elementos):
        response = webhook(fulfillment_text)
    else:
        response = fulfillment_text
    response_text = {"message":response}
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