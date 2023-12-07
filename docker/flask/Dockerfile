# Webserver
FROM python:3.12

# Copiar el código de la aplicación
COPY . /flask

# Cambiar al directorio del servidor web
WORKDIR /flask

# Instalar Flask
RUN pip install flask confluent_kafka google-cloud-dialogflow pusher sqlalchemy pandas psycopg2-binary tabulate

# Ejecutar servidor web
CMD ["python", "app.py"]
