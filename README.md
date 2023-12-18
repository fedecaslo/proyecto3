# Proyecto 3 - Instrucciones de configuración

Este README proporciona instrucciones paso a paso para configurar el entorno y replicar la arquitectura propuesta.

En nuestra arquitectura, la parte principal será la base de datos donde almacenaremos todos los datos, y hemos elegido PostgreSQL para este propósito. Utilizaremos Flask para desarrollar una aplicación que pueda recibir archivos CSV siempre que se proporcione la contraseña correcta, y luego enviará estos archivos a un productor de Kafka. Además, los patinetes también pueden enviar información directamente a Kafka a través de los productores.

La información que requiera procesamiento será manejada por Apache Airflow. Este componente recogerá datos de los consumidores de Kafka, procesará las consultas necesarias y los incorporará a la base de datos. En Flask, hemos implementado un webhook utilizando ngrok para conectar el chatbot de Dialogflow. Flask tiene acceso directo a la base de datos, lo que le permite enviar la información de las consultas al chatbot.

Finalmente, toda la información almacenada en PostgreSQL puede ser visualizada en Grafana, donde hemos configurado alertas que se envían a través de Teams.

<img width="947" alt="MicrosoftTeams-image" src="https://github.com/fedecaslo/proyecto3/assets/72439774/394f5add-645a-4b3e-a62a-54bc1fbe3257">


## 1. Iniciar Servicios con Docker Compose
Ejecuta el siguiente comando para iniciar los servicios definidos en el archivo `docker-compose.yml`:

```bash
docker-compose up
```

## 2. Creación de usuario y configuración de Apache Airflow
Ejecuta el archivo `start.sh` utilizando el siguiente comando en una terminal nueva:

```bash
chmod +x ./start.sh
./start.sh
```
Este script configura y prepara Apache Airflow con los comando necesarios.

Tras realizar esto, abre tu navegador y accede a `localhost:8080`. Inicia sesión con las siguientes credenciales:

* User: admin
* Password: pass

Una vez hayas iniciado sesión, podrás acceder al panel de control de Apache Airflow. Dentro del panel de control de Airflow, encontrarás dos DAGs preconfigurados que puedes activar para realizar tareas específicas de manera automática:

1. `cargar_csv_a_postgres`: Un DAG simple para cargar un archivo CSV en PostgreSQL y realizar una serie de consultas que crean nuevas tablas especificas para cada consulta. Se ejecuta cada hora para mantener actualizadas las consultas.
2. `kafka_to_postgres`: Un DAG simple para leer los mensajes de un topic de kafka y los guarda en una tabla llamada `rome_table` en una base de datos de PostgreSQL. Se actualiza cada 1 minuto para mantener la base de datos lo más cercana a la ingesta en tiempo real posible.

Para activar el DAG haz clic en el botón `Trigger DAG`. Con estos pasos, habrás configurado y activado los DAGs en Apache Airflow, permitiéndote automatizar las tareas descritas anteriormente.

## 3. Envío de datos de los patinetes
Ejecuta el archivo `patinete.sh` utilizando el siguiente comando en una terminal nueva:

```bash
chmod +x ./patinete.sh
./patinetes.sh
```
Este script simula el envío de nuevos datos al topic de kafka por parte de algunos patinetes de la flota. Estos datos han sido generados artificialmente mediante un modelo generativo, CTGAN (Conditional Tabular Generative Adversarial Network). Para poder generar datos nuevos, descarga el [modelo](https://drive.google.com/file/d/1tuxLFPqbpbCkojnhQBXjF_bNz8-0fx0s/view?usp=sharing) e inclúyelo en la carpeta datos_sinteticos. Una vez que esté dentro, ejecuta el código `patinetes.py` dentro de esa carpeta. Los datos que generes se guardarán en `prueba.csv`.

## 4. Envío de lote de datos a través de flask
Abre tu navegador y accede a `localhost:5001`. En la página HTML que aparecerá, podrás seleccionar un archivo CSV desde tu ordenador arrastrándolo a la página o utilizando el botón de selección de archivos. Después de seleccionar el archivo, se te solicitará una contraseña.Ingresa la contraseña requerida:

* Contraseña: pass

Una vez ingresada la contraseña, podrás hacer clic en el botón para enviar el lote de datos al topic de Kafka, lo que actualizará la base de datos PostgreSQL con la información del archivo CSV una vez se ejecute de nuevo el DAG `kafka_to_postgres` programado cada 1 minuto.

## 4. Conectar el chatbot a la API de flask
Para conectar el chatbot a la API de Flask, sigue estos pasos:

1. Abre una nueva terminal y ejecuta el siguiente comando para iniciar ngrok:

```bash
ngrok http 5001
```
Esto abrirá una nueva ventana de ngrok, donde deberás fijarte en la fila de `Forwarding` para encontrar la URL que comienza con `https://`. Copia esa URL, ya que la necesitarás para configurar el webhook en Dialogflow.

2. Accede a la consola de Dialogflow y selecciona tu proyecto.

3. En la sección de configuración, busca la opción de `Fulfillment` o `Webhook` y habilita el webhook.

4. Pega la URL de ngrok que copiaste en el paso 1 en el campo de URL del webhook.

5. Guarda la configuración.

Con estos pasos, has configurado el webhook en Dialogflow para apuntar a la API de Flask a través de ngrok.

Ahora, para interactuar con MR.Bin, abre tu navegador y accede a `localhost:5001/chat`. Desde allí, podrás comenzar a interactuar con MR.Bin a través del chatbot conectado a la API de Flask.

## 6. Configurar Grafana
Abre Grafana en tu navegador en `localhost:3000` e añade una nueva fuente de datos PostgreSQL con los siguientes ajustes:

* Host: postgres:5432
* SSL: Deshabilitar
* Usuario/Contraseña/Base de Datos: admin/admin/rome
* Versión: PostgreSQL 12+

## 7. Configurar Consulta en Grafana
En Grafana, ve al menú principal y selecciona `Folder` para crear uno nuevo. Luego, dentro del nuevo folder, selecciona `Dashboard` para crear un nuevo dashboard.

Para editar el dashboard recién creado y selecciona `Add Panel` para agregar un nuevo panel. En la configuración del panel, selecciona `Query` y elige `SQL` como tipo de consulta. Copia y pega la siguiente consulta SQL en el campo de consulta:

```sql
SELECT
  "Fecha" AS "time",
  "idS" AS metric,
  bateria_restante
FROM bateria_patinete
WHERE
  bateria_restante<= 20
```
Esta consulta selecciona la fecha, el ID del patinete y la batería restante de la tabla bateria_patinete donde la batería es inferior o igual al 20%. Guarda el panel y el dashboard.

## 8. Configurar las alertas de Grafana

Para configurar alertas en Grafana y recibir notificaciones en Microsoft Teams, sigue estos pasos:

1. Crear una Template en Connection Points
Ve a `Connection Points` en Grafana.Crea una nueva template con el nombre `Bateria_baja`.

En el cuerpo del mensaje, utiliza el siguiente formato:
 
```bash
{{define "Bateria_baja"}}
**Alerta de Batería Baja**

Se han detectado uno o más patinetes con un nivel de batería por debajo del 20%. Aquí están todos los detalles:

{{end}}
```
2. Configurar el Punto de Conexión para Microsoft Teams

En `Connection Points`, selecciona la opción para configurar un nuevo punto de conexión. Elige `Microsoft Teams` como el tipo de conexión.En el campo `Message`, introduce `{{template "Bateria_baja"}}``.

Introduce la URL del webhook configurado en Microsoft Teams. 

3. Para obtener la URL del webhook en Microsoft Teams:
Ve al canal donde deseas recibir las alertas. Haz clic en los tres puntos `(···)` junto al nombre del canal y selecciona `Conectar a un flujo`.Configura un conector de entrada y copia la URL del webhook generada.

4. Configurar la Alerta en el Panel de Grafana

Ve al folder y al panel previamente creados.Selecciona "Configuración de alerta" y crea una nueva alerta con la siguiente configuración:

```bash
B: When A is below 20
```
Define las condiciones de la alerta para activarse cuando el nivel de batería es inferior al 20%.

5. Monitorear las Alertas

Cuando se active una alerta, recibirás un mensaje en el canal de Microsoft Teams configurado. Desde el mensaje en Teams, podrás acceder a la consulta y ver los IDs de los patinetes con batería baja.

Siguiendo estos pasos, habrás configurado alertas en Grafana que enviarán notificaciones a Microsoft Teams cuando se detecte un nivel de batería bajo en los patinetes.
