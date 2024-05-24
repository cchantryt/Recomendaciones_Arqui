from flask import Flask
from app.database import init_db
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    load_dotenv()  # Cargar variables de entorno desde .env si existe

    init_db(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
