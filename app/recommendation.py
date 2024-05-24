import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.database import get_db_connection

def generate_recommendations(data):
    conn = get_db_connection()

    # Consultamos la base de datos para obtener las compras de los usuarios
    query = "SELECT user_id, product_id FROM purchases"
    purchases = pd.read_sql_query(query, conn)

    # Creamos una matriz de usuario-producto
    user_product_matrix = purchases.pivot_table(index='user_id', columns='product_id', aggfunc='size', fill_value=0)

    # Calculamos la similitud del coseno entre productos
    product_similarity = cosine_similarity(user_product_matrix.T)

    # Convertimos la matriz de similitud en un DataFrame
    product_similarity_df = pd.DataFrame(product_similarity, index=user_product_matrix.columns, columns=user_product_matrix.columns)

    # Obtenemos el ID del usuario del que queremos hacer la recomendación
    user_id = data['user_id']
    
    # Obtenemos los productos que el usuario ha comprado
    user_products = user_product_matrix.loc[user_id]
    user_products = user_products[user_products > 0].index.tolist()

    # Calculamos las recomendaciones
    recommendations = []
    for product in user_products:
        similar_products = product_similarity_df[product].sort_values(ascending=False).index.tolist()
        recommendations.extend(similar_products)

    # Filtramos las recomendaciones para eliminar los productos que el usuario ya ha comprado
    recommendations = [product for product in recommendations if product not in user_products]

    # Nos quedamos con las 3 recomendaciones más similares
    recommendations = recommendations[:3]

    conn.close()
    return {"recommendations": recommendations}
