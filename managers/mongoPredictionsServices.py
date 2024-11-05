from models.mongoPredictionsModel import PredictionModel

class PredictionService:
    def __init__(self):
        self.prediction_model = PredictionModel()

    def savePrediction(self, input_data, prediction_response):
        """
        Procesa y guarda la predicción.
        """
        return self.prediction_model.savePrediction(input_data, prediction_response)
