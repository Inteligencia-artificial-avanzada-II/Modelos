import os
from dotenv import load_dotenv
from utils.utils import *

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Configuración de la aplicación."""
    ENVIRONMENT = os.getenv("FLASK_ENV", "DEV")
    MONGO_URI = os.getenv("MONGO_DB", "mongodb://localhost:27017/mydatabase")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    FLASK_HOST = os.getenv(f'FLASK_HOST_{ENVIRONMENT}', "127.0.0.1")
    FLASK_PORT = os.getenv(f"FLASK_PORT_{ENVIRONMENT}", "5000")
    FLASK_DEBUG = str_to_bool(os.getenv(f"FLASK_DEBUG_{ENVIRONMENT}", "True"))
    RUTA_ARCHIVO_ORDENES = os.getenv("RUTA_ARCHIVO_ORDENES", "")