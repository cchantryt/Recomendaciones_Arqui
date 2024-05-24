import psycopg2
import os
import pandas as pd

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        sslmode=os.getenv('POSTGRES_SSLMODE')
    )
    return conn

def init_db(app):
    with app.app_context():
        conn = get_db_connection()
        conn.close()