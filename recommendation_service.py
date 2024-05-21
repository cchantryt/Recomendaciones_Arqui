from flask import Flask, request, jsonify
import psycopg2
import pandas as pd
from surprise import Dataset, Reader, KNNWithMeans
import os
 
app = Flask(__name__)
 
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    return jsonify(generate_recommendations(data))
 
def generate_recommendations(data):
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
 
    query = "SELECT user_id, product_id, 1 FROM purchases"
    purchases = pd.read_sql_query(query, conn)
 
    reader = Reader(rating_scale=(1, 1))
    data = Dataset.load_from_df(purchases[['user_id', 'product_id', 'purchased']], reader)
 
    trainset = data.build_full_trainset()
    algo = KNNWithMeans(sim_options={'name': 'pearson_baseline', 'user_based': False})
    algo.fit(trainset)
 
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)
 
    user_id = data.raw_ratings[0][0]
    user_predictions = [pred for pred in predictions if pred.uid == user_id]
 
    user_predictions.sort(key=lambda x: x.est, reverse=True)
 
    top3_recommendations = user_predictions[:3]
    recommendations = {"recommendations": [pred.iid for pred in top3_recommendations]}
 
    conn.close()
    return recommendations
 
@app.route('/users', methods=['GET'])
def get_users():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )
 
    query = "SELECT * FROM Users"
    users = pd.read_sql_query(query, conn)
 
    conn.close()
    return users.to_json(orient='records')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
