import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.database import get_db_connection

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
        return {"recommendations": []}
    
    order_ids = tuple(map(int, orders_df['OrderId']))

    # Obtener los detalles de las órdenes
    query_order_details = 'SELECT "ProductId" FROM "OrderDetails" WHERE "OrderId" IN %s'
    order_details_df = pd.read_sql_query(query_order_details, conn, params=[order_ids])

    if order_details_df.empty:
        return {"recommendations": []}
    
    # Obtener la lista de productos comprados
    purchased_product_ids = order_details_df['ProductId'].unique()
    purchased_product_ids = tuple(map(int, purchased_product_ids))

    # Obtener productos similares (aquí debes definir tu lógica de similitud)
    query_products = 'SELECT "ProductId" FROM "Products" WHERE "ProductId" NOT IN %s ORDER BY RANDOM() LIMIT 3'
    recommended_products_df = pd.read_sql_query(query_products, conn, params=[purchased_product_ids])

    # Cerramos la conexión a la base de datos y devolvemos las recomendaciones
    conn.close()
    
    recommendations = {"recommendations": recommended_products_df['ProductId'].tolist()}
    return recommendations
