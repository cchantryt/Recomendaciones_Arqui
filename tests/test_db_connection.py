import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        sslmode=os.getenv('POSTGRES_SSLMODE')
    )
    print("Conexión exitosa")
    conn.close()
except Exception as e:
    print(f"Error de conexión: {e}")
