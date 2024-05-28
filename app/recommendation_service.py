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

    # Consultamos la base de datos para obtener el "UserId" a partir del "WebId"
    webid = data['webid']
    query = 'SELECT "UserId" FROM "Users" WHERE "WebId" = %s'
    userid = pd.read_sql_query(query, conn, params=[webid])

    # Si el "WebId" no existe, devolvemos un error
    if userid.empty:
        return {"error": "Invalid WebId"}
    user_id = int(userid.iloc[0]['UserId'])

    # Consultamos las "Orders" que tiene el "UserId"
    query = 'SELECT "OrderId" FROM "Orders" WHERE "UserId" = %s'
    orders_df = pd.read_sql_query(query, conn, params=[user_id])

    # Consultamos los "ProductId" de los productos comprados
    order_ids = orders_df['OrderId'].tolist()
    query = f'SELECT "ProductId" FROM "OrderDetails" WHERE "OrderId" IN ({", ".join(map(str, order_ids))})'
    product_ids = pd.read_sql_query(query, conn)['ProductId'].tolist()

    # Si el usuario no ha comprado nada, devolvemos los productos más populares
    if not product_ids:
        query = 'SELECT "ProductId", COUNT(*) as purchase_count FROM "OrderDetails" GROUP BY "ProductId" ORDER BY purchase_count DESC LIMIT 3'
        popular_products = pd.read_sql_query(query, conn)
        return popular_products['ProductId'].tolist()

    # Consultamos los productos que ha comprado
    query = f'SELECT * FROM "Products" WHERE "ProductId" IN ({", ".join(map(str, product_ids))})'
    purchases = pd.read_sql_query(query, conn)

    # Preparamos los datos para el algoritmo de recomendación
    reader = Reader(rating_scale=(1, 1))
    data = Dataset.load_from_df(purchases[['UserId', 'ProductId', 'purchased']], reader)

    # Entrenamos el algoritmo de recomendación
    trainset = data.build_full_trainset()
    algo = KNNWithMeans(sim_options={'name': 'pearson_baseline', 'user_based': False})
    algo.fit(trainset)

    # Generamos las predicciones
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    # Filtramos las predicciones para el usuario solicitado
    user_predictions = [pred for pred in predictions if pred.uid == userid]

    # Ordenamos las predicciones por estimación y nos quedamos con las 3 mejores
    user_predictions.sort(key=lambda x: x.est, reverse=True)
    top3_recommendations = user_predictions[:3]
    recommendations = {"recommendations": [pred.iid for pred in top3_recommendations]}

    # Cerramos la conexión a la base de datos y devolvemos las recomendaciones
    conn.close()
    return recommendations

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)