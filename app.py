from flask import Flask
from pymongo import MongoClient
from config import Config
from database.mongoConnection import getDatabase
from controllers.mongoPredictionsController import mongoPredictionsBp

app = Flask(__name__)
app.config.from_object(Config)
print(app.config['FLASK_HOST'])

# Configuración de la conexión a MongoDB
mongo_client = MongoClient(app.config['MONGO_URI'])
db = getDatabase()

app.register_blueprint(mongoPredictionsBp, url_prefix="/predictions")

if __name__ == "__main__":
    app.run(host=app.config['FLASK_HOST'], port=int(app.config['FLASK_PORT']), debug=bool(app.config['FLASK_DEBUG']))
