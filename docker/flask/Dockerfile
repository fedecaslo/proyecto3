# Webserver
FROM python:3.12

# Copiar el código de la aplicación
COPY . /flask

# Cambiar al directorio del servidor web
WORKDIR /flask

# Instalar Flask
RUN pip install flask confluent_kafka

# Ejecutar servidor web
CMD ["python", "app.py"]
