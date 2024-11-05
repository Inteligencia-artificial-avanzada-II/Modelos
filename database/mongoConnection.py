from pymongo import MongoClient
from config import Config


def getMongoClient():
    """Devuelve una instancia de MongoClient conectada a MongoDB."""
    client = MongoClient(Config.MONGO_URI)
    return client


def getDatabase():
    """Devuelve la base de datos especificada en Config."""
    client = getMongoClient()
    db = client.get_database()
    return db