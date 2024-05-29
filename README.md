# Recomendaciones Arqui

Este repositorio contiene el código fuente de la aplicación de recomendaciones construida con Flask, que utiliza un algoritmo de filtrado colaborativo para generar recomendaciones de productos basadas en el historial de compras de los usuarios.

## Características

- **API REST**: La aplicación expone una API REST que permite obtener recomendaciones de productos.
- **Filtrado colaborativo**: Utiliza el algoritmo de filtrado colaborativo KNNWithMeans de la biblioteca scikit-surprise para generar recomendaciones.
- **Base de datos PostgreSQL**: Almacena información de usuarios, órdenes y detalles de órdenes en una base de datos PostgreSQL.

## Configuración
La aplicación se configura a través de variables de entorno, las cuales se pueden especificar en un archivo `.env`. Un ejemplo de las variables necesarias se muestra a continuación:

env
POSTGRES_USER=default
POSTGRES_HOST=ep-twilight-thunder-a44l3m22-pooler.us-east-1.aws.neon.tech
POSTGRES_PASSWORD=gRrNo7CzZcw4
POSTGRES_DATABASE=verceldb
POSTGRES_PORT=5432
POSTGRES_SSLMODE=require


## Despliegue
El archivo render.yaml contiene la configuración necesaria para desplegar la aplicación en Render, incluyendo la especificación del entorno de ejecución, comandos de construcción y variables de entorno.
```yaml
services:
  - type: web
    runtime: python
    name: recomendaciones-arqui
    plan: free
    buildCommand: |
      apt-get update && apt-get install -y build-essential
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: gunicorn -w 3 run:app
    envVars:
      - key: DATABASE_URL
        value: postgres://...
      - key: DB_NAME
        value: verceldb
      - key: DB_USER
        value: default
      - key: DB_PASSWORD
        value: ...
      - key: DB_HOST
        value: ...
      - key: DB_PORT
        value: 5432
```
## Uso
Para obtener recomendaciones, se debe enviar una solicitud POST a la ruta /recommend de la API, incluyendo el webid del usuario en el cuerpo de la solicitud.
```
import requests

data = {'webid': 'user_webid'}
response = requests.post('http://<your-app-url>/recommend', json=data)
recommendations = response.json()
```
## Desarrollo
Para iniciar el desarrollo local, asegúrese de tener instaladas todas las dependencias especificadas en requirements.txt.
```
pip install -r requirements.txt
```
Luego, puede iniciar la aplicación Flask ejecutando:
```
python run.py
```
