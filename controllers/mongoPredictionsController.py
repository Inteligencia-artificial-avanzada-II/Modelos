from flask import Blueprint, request, Response
import json
from managers.mongoPredictionsServices import PredictionService

mongoPredictionsBp = Blueprint("mongoPredictionsBp", __name__)
prediction_service = PredictionService()


@mongoPredictionsBp.route("/predict", methods=["POST"])
def savePrediction():
    data = request.json

    # Validación de datos de entrada
    input_data = data.get("input_data")
    prediction_response = data.get("prediction_response")
    if not input_data or not prediction_response:
        return Response(
            response=json.dumps(
                {"error": "Datos de entrada o respuesta de predicción faltantes"}),
            status=400,
            mimetype="application/json"
        )

    try:
        # Guarda la predicción usando el servicio
        prediction_id = prediction_service.savePrediction(
            input_data, prediction_response)
        return Response(
            response=json.dumps(
                {"message": "Predicción guardada", "prediction_id": prediction_id}),
            status=201,
            mimetype="application/json"
        )
    except Exception as e:
        # Manejo de errores en caso de fallo
        return Response(
            response=json.dumps(
                {"error": f"Ocurrió un error al guardar la predicción: {str(e)}"}),
            status=500,
            mimetype="application/json"
        )
