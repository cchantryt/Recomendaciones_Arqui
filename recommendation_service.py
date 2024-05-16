from flask import Flask, request, jsonify
from sklearn.neighbors import NearestNeighbors
import mysql.connector
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
import pandas as pd
from surprise import Dataset, Reader, KNNWithMeans
from surprise.model_selection import train_test_split

app = Flask(__name__)
@app.route('/recommend', methods=['POST'])
def recommend():
    # Recibe los datos del pedido del usuario
    data = request.get_json()
    return jsonify(generate_recommendations(data))

def generate_recommendations(data):
    # Conexión a la base de datos
    cnx = mysql.connector.connect(user='your_username', password='your_password',
                                  host='127.0.0.1',
                                  database='your_database')
    cursor = cnx.cursor()

    # Consulta a la base de datos para obtener las compras de los usuarios
    query = ("SELECT user_id, product_id, 1 FROM purchases")
    cursor.execute(query)

    # Carga los datos en un DataFrame de pandas
    purchases = pd.DataFrame(cursor.fetchall(), columns=['user_id', 'product_id', 'purchased'])

    # Carga los datos de las compras en un conjunto de datos de Surprise
    data = Dataset.load_from_df(purchases)

    # Entrena un modelo de filtrado colaborativo basado en ítems
    trainset = data.build_full_trainset()
    algo = KNNWithMeans(sim_options={'name': 'pearson_baseline', 'user_based': False})
    algo.fit(trainset)

    # Obtiene las recomendaciones para el usuario
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    # Filtra las predicciones para el usuario especificado
    user_id = data[0]['userId']
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
