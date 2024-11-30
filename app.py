from flask import Flask
from pymongo import MongoClient
from config import Config
from database.mongoConnection import getDatabase
from controllers.mongoPredictionsController import mongoPredictionsBp
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
# Habilitar CORS en toda la aplicación
CORS(app)

# Configuración de la conexión a MongoDB
mongo_client = MongoClient(app.config['MONGO_URI'])
db = getDatabase()

# Registramos nuestra ruta que redirigirá hacia nuestro controlador de predicciones
app.register_blueprint(mongoPredictionsBp, url_prefix="/predictions")

if __name__ == "__main__":
    # Corre el servidor de flask
    app.run(host=app.config['FLASK_HOST'], port=int(app.config['FLASK_PORT']), debug=bool(app.config['FLASK_DEBUG']))
