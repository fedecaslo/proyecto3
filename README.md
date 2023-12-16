# Proyecto 3 - Instrucciones de configuración

Este README proporciona instrucciones paso a paso para configurar el entorno y replicar la arquitectura propuesta.

En nuestra arquitectura, la parte prncipal será la base de datos donde almacenaremos todos los datos, y hemos elegido PostgreSQL para este propósito. Utilizaremos Flask para desarrollar una aplicación que pueda recibir archivos CSV siempre que se proporcione la contraseña correcta, y luego enviará estos archivos a un productor de Kafka. Además, los patinetes también pueden enviar información directamente a Kafka a través de los productores.

La información que requiera procesamiento será manejada por Apache Airflow. Este componente recogerá datos de los consumidores de Kafka, procesará las consultas necesarias y los incorporará a la base de datos. En Flask, hemos implementado un webhook utilizando ngrok para conectar el chatbot de Dialogflow. Flask tiene acceso directo a la base de datos, lo que le permite enviar la información de las consultas al chatbot.

Finalmente, toda la información almacenada en PostgreSQL puede ser visualizada en Grafana, donde hemos configurado alertas que se envían a través de Teams.

<img width="947" alt="MicrosoftTeams-image" src="https://github.com/fedecaslo/proyecto3/assets/72439774/394f5add-645a-4b3e-a62a-54bc1fbe3257">


## 1. Iniciar Servicios con Docker Compose
Ejecuta el siguiente comando para iniciar los servicios definidos en el archivo `docker-compose.yml`:

```bash
docker-compose up
```

## 2. Acceder a la Consola de PostgreSQL
Para acceder a la consola de PostgreSQL dentro del contenedor, utiliza los siguientes comandos:

```bash
docker exec -it postgres /bin/bash
```
Una vez dentro de la consola del contenedor de postgres:
```bash
psql -U admin rome
```

## 3. Crear Tabla en PostgreSQL
Crea la tabla "rome_table" ejecutando la siguiente consulta SQL:

```sql
CREATE TABLE rome_table (
    idS VARCHAR(255),
    tsO TIMESTAMP,
    tsD TIMESTAMP,
    price NUMERIC(10,4),
    tt INTEGER,
    dis NUMERIC(15,6),
    vel NUMERIC(15,6),
    lonO NUMERIC(10,6),
    latO NUMERIC(10,6),
    lonD NUMERIC(10,6),
    latD NUMERIC(10,6)
);
```
## 4. Copiar Datos desde CSV
Copia los datos desde el archivo CSV en la tabla rome_table con la siguiente consulta SQL:

```sql
COPY rome_table (ids, tso, tsd, price, tt, dis, vel, lono, lato, lond, latd) FROM '/docker-entrypoint-initdb.d/rome_u_journeys.csv' DELIMITER ',' CSV HEADER;
```
## 5. Configurar Grafana
Abre Grafana en tu navegador en `localhost:3000` e añade una nueva fuente de datos PostgreSQL con los siguientes ajustes:

* Host: postgres:5432
* SSL: Deshabilitar
* Usuario/Contraseña/Base de Datos: admin/admin/rome
* Versión: PostgreSQL 12+

## 6. Configurar Consulta en Grafana
Edita tu dashboard en Grafana y utiliza la siguiente consulta SQL para visualizar datos específicos (en este caso, para el identificador 'A0H4'):
```sql
SELECT
  tso AS "time",
  price
FROM rome_table
WHERE
  ids='A0H4'
```
## 7. Flask
