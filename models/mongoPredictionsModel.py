from database.mongoConnection import getDatabase


class PredictionModel:
    def __init__(self):
        # Accede a la base de datos y selecciona la colección `predictions`
        self.db = getDatabase()
        self.collection = self.db["predictions"]

    def savePrediction(self, inputData, predictionResponse):
        """
        Guarda una predicción en la base de datos.

        :param inputData: Diccionario con los datos de entrada para la predicción.
        :param predictionResponse: Diccionario con el resultado de la predicción.
        :return: El ID del documento insertado.
        """
        prediction_record = {
            "inputData": inputData,
            "predictionResponse": predictionResponse
        }
        result = self.collection.insert_one(prediction_record)
        return result
