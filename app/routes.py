from flask import Blueprint, jsonify, request
from app.recommendation import generate_recommendations
from app.database import get_db_connection
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    recommendations = generate_recommendations(data)
    return jsonify(recommendations)

@main.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()

    # Consultamos la base de datos para obtener todos los usuarios
    query = "SELECT * FROM Users"
    users = pd.read_sql_query(query, conn)

    # Cerramos la conexión a la base de datos y devolvemos los usuarios como una respuesta JSON
    conn.close()
    return users.to_json(orient='records')
