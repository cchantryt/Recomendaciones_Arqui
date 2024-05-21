from flask import Flask, request, jsonify
import psycopg2
import pandas as pd
from surprise import Dataset, Reader, KNNWithMeans

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    # Recibe los datos del pedido del usuario
    data = request.get_json()
    return jsonify(generate_recommendations(data))

def generate_recommendations(data):
    # Conexión a la base de datos PostgreSQL
    cnx = psycopg2.connect(
        dbname='verceldb',
        user='default',
        password='gRrNo7CzZcw4',
        host='ep-twilight-thunder-a44l3m22-pooler.us-east-1.aws.neon.tech',
        port='5432',
        sslmode='require'
    )
    cursor = cnx.cursor()

    # Consulta a la base de datos para obtener las compras de los usuarios
    query = "SELECT user_id, product_id, 1 FROM purchases"
    cursor.execute(query)

    # Carga los datos en un DataFrame de pandas
    purchases = pd.DataFrame(cursor.fetchall(), columns=['user_id', 'product_id', 'purchased'])

    # Carga los datos de las compras en un conjunto de datos de Surprise
    reader = Reader(rating_scale=(1, 1))
    data = Dataset.load_from_df(purchases[['user_id', 'product_id', 'purchased']], reader)

    # Entrena un modelo de filtrado colaborativo basado en ítems
    trainset = data.build_full_trainset()
    algo = KNNWithMeans(sim_options={'name': 'pearson_baseline', 'user_based': False})
    algo.fit(trainset)

    # Obtiene las recomendaciones para el usuario
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    # Filtra las predicciones para el usuario especificado
    user_id = data.raw_ratings[0][0]
    user_predictions = [pred for pred in predictions if pred.uid == user_id]

    # Ordena las predicciones por calificación estimada
    user_predictions.sort(key=lambda x: x.est, reverse=True)

    # Devuelve las 3 principales recomendaciones
    top3_recommendations = user_predictions[:3]
    recommendations = {"recommendations": [pred.iid for pred in top3_recommendations]}

    # Cierre de la conexión a la base de datos
    cursor.close()
    cnx.close()

    return recommendations

@app.route('/users', methods=['GET'])
def get_users():
    # Conexión a la base de datos PostgreSQL
    cnx = psycopg2.connect(
        dbname='verceldb',
        user='default',
        password='gRrNo7CzZcw4',
        host='ep-twilight-thunder-a44l3m22-pooler.us-east-1.aws.neon.tech',
        port='5432',
        sslmode='require'
    )
    cursor = cnx.cursor()

    # Consulta a la base de datos para obtener los usuarios
    query = "SELECT * FROM Users"
    cursor.execute(query)

    # Carga los datos en un DataFrame de pandas
    users = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    # Cierre de la conexión a la base de datos
    cursor.close()
    cnx.close()

    # Devuelve los usuarios en formato JSON
    return users.to_json(orient='records')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
