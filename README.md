# Proyecto 3 - Instrucciones de configuración

Este README proporciona instrucciones paso a paso para configurar el entorno y replicar la arquitectura propuesta.

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
