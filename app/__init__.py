from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Carga las variables de entorno desde el archivo .env
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    from app.database import init_db
    init_db(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
