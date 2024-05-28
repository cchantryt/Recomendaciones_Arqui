import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.database import get_db_connection
from surprise import Reader, Dataset, KNNWithMeans
from surprise.model_selection import train_test_split


def generate_recommendations(webid):
    conn = get_db_connection()
    
    # Obtener el UserId a partir del Webid
    query_user = 'SELECT "UserId" FROM "Users" WHERE "Webid" = %s'
    user_id_df = pd.read_sql_query(query_user, conn, params=[webid])
    
    if user_id_df.empty:
        return {"error": "Invalid webid"}
    
    user_id = int(user_id_df.iloc[0]['UserId'])

    # Obtener las órdenes del usuario
    query_orders = 'SELECT "OrderId" FROM "Orders" WHERE "UserId" = %s'
    orders_df = pd.read_sql_query(query_orders, conn, params=[user_id])
    
    if orders_df.empty:
         # Si el usuario no ha realizado ninguna orden, recomendamos los 3 productos más vendidos
        query_most_sold = 'SELECT "ProductId", COUNT(*) as purchase_count FROM "OrderDetails" GROUP BY "ProductId" ORDER BY purchase_count DESC LIMIT 3'
        most_sold_df = pd.read_sql_query(query_most_sold, conn)
        recommendations = {"recommendations": most_sold_df['ProductId'].tolist()}
        return recommendations
    
    order_ids = tuple(map(int, orders_df['OrderId']))

    # Obtener los detalles de las órdenes
    query_order_details = 'SELECT "ProductId" FROM "OrderDetails" WHERE "OrderId" IN %s'
    order_details_df = pd.read_sql_query(query_order_details, conn, params=[order_ids])

    # Obtener todas las interacciones usuario-producto
    query_interactions = 'SELECT "UserId", "ProductId", COUNT(*) as purchase_count FROM "OrderDetails" JOIN "Orders" ON "OrderDetails"."OrderId" = "Orders"."OrderId" GROUP BY "UserId", "ProductId"'
    interactions_df = pd.read_sql_query(query_interactions, conn)

    # Crear un objeto Reader y un objeto Dataset
    reader = Reader(rating_scale=(0, interactions_df['purchase_count'].max()))
    data = Dataset.load_from_df(interactions_df[['UserId', 'ProductId', 'purchase_count']], reader)

    # Dividir los datos en un conjunto de entrenamiento y un conjunto de prueba
    trainset, testset = train_test_split(data, test_size=0.2)

    # Entrenar un algoritmo de filtrado colaborativo basado en ítems
    algo = KNNWithMeans(sim_options={'name': 'cosine', 'user_based': False})
    algo.fit(trainset)

    # Generar recomendaciones para el usuario
    user_inner_id = trainset.to_inner_uid(user_id)
    user_neighbors = algo.get_neighbors(user_inner_id, k=3)
    user_neighbors = (trainset.to_raw_iid(inner_id) for inner_id in user_neighbors)

    recommendations = {"recommendations": list(user_neighbors)}
    return recommendations
