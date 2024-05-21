# Importamos las librerías necesarias
from flask import Flask, request, jsonify
import psycopg2
import pandas as pd
from surprise import Dataset, Reader, KNNWithMeans
import os
 
# Creamos una nueva aplicación Flask
app = Flask(__name__)
 
# Definimos una ruta '/recommend' que acepta solicitudes POST
@app.route('/recommend', methods=['POST'])
def recommend():
    # Obtenemos los datos JSON de la solicitud
    data = request.get_json()
    # Generamos las recomendaciones y las devolvemos como una respuesta JSON
    return jsonify(generate_recommendations(data))
 
# Función para generar recomendaciones
def generate_recommendations(data):
    # Nos conectamos a la base de datos
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
 
    # Consultamos la base de datos para obtener las compras de los usuarios
    query = "SELECT user_id, product_id, 1 FROM purchases"
    purchases = pd.read_sql_query(query, conn)
 
    # Preparamos los datos para el algoritmo de recomendación
    reader = Reader(rating_scale=(1, 1))
    data = Dataset.load_from_df(purchases[['user_id', 'product_id', 'purchased']], reader)
 
    # Entrenamos el algoritmo de recomendación
    trainset = data.build_full_trainset()
    algo = KNNWithMeans(sim_options={'name': 'pearson_baseline', 'user_based': False})
    algo.fit(trainset)
 
    # Generamos las predicciones
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)
 
    # Filtramos las predicciones para el usuario solicitado
    user_id = data.raw_ratings[0][0]
    user_predictions = [pred for pred in predictions if pred.uid == user_id]
 
    # Ordenamos las predicciones por estimación y nos quedamos con las 3 mejores
    user_predictions.sort(key=lambda x: x.est, reverse=True)
    top3_recommendations = user_predictions[:3]
    recommendations = {"recommendations": [pred.iid for pred in top3_recommendations]}
 
    # Cerramos la conexión a la base de datos y devolvemos las recomendaciones
    conn.close()
    return recommendations
 
# Definimos una ruta '/users' que acepta solicitudes GET
@app.route('/users', methods=['GET'])
def get_users():
    # Nos conectamos a la base de datos
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
 
    # Consultamos la base de datos para obtener todos los usuarios
    query = "SELECT * FROM Users"
    users = pd.read_sql_query(query, conn)
 
    # Cerramos la conexión a la base de datos y devolvemos los usuarios como una respuesta JSON
    conn.close()
    return users.to_json(orient='records')

# Si el script se ejecuta directamente (no importado), iniciamos la aplicación Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)