from flask import Blueprint, request, Response
import requests
import datetime
import json
from managers.mongoPredictionsServices import PredictionService
from model.objects.remolques import Remolque
from model.utils.load_data_as_objects import cargar_ordenes
from model import mainModel

from config import Config

mongoPredictionsBp = Blueprint("mongoPredictionsBp", __name__)
prediction_service = PredictionService()


@mongoPredictionsBp.route("/predict", methods=["POST"])
def savePrediction():
    remolques = []
    ordenes = cargar_ordenes(f'{Config.RUTA_ARCHIVO_ORDENES}')
    data = request.json
    headersToken = request.headers.get('Authorization')
    token = headersToken.split('Token ')[1]

    headersForSent = {
        "Authorization": f"Token {token}"
    }

    # Validación de datos de entrada
    input_data = data.get("input_data")

    if not input_data:
        return Response(
            response=json.dumps(
                {"error": "Datos de entrada o respuesta de predicción faltantes"}),
            status=400,
            mimetype="application/json"
        )

    try:
        apiOrdenContenedorId = f'{Config.RUTA_BACK}/orden/consultarQrUrl'
        apiFosasGetAll = f'{Config.RUTA_BACK}/fosa/consultarTodos'
        apiOrdenMongoId = f'{Config.RUTA_BACK}/ordenmongo/consultar'
        responseFosas = requests.get(apiFosasGetAll)
        dataFosas = json.loads(json.dumps(responseFosas.json()))
        allFosas = dataFosas[0]['fosas']

        for fosa in allFosas:
            dailyFosa = fosa['daily']
            fechaNow = datetime.now().strftime("%d/%m/%Y")

            dailyFechaData = dailyFosa[fechaNow]
            contenedorIdKey = next(iter(dailyFechaData.keys()))
            contenedorId = contenedorIdKey.split('-')[0]

            responseOrdenData = requests.get(f'{apiOrdenContenedorId}/{contenedorId}', headers=headersForSent)

            ordenSqlData = responseOrdenData.json()['data'] if responseOrdenData.json().get('data') else None
            if not ordenSqlData:
                continue
            ordenMongoId = ordenSqlData.get('idMongoProductos') if ordenSqlData else None
            responseOrdenMongoData = requests.get(f'{apiOrdenMongoId}/{ordenMongoId}', headers=headersForSent) if ordenMongoId else None
            ordenMongoData = responseOrdenMongoData.json().get('data') if responseOrdenMongoData else None
            origen = ordenSqlData.get('origen') if ordenSqlData else None
            fechaSalida = ordenMongoData.get('fechaSalida') if ordenMongoData else None
            productosContenido = ordenMongoData.get('products') if ordenMongoData else None

            # Creamos la lista de los camiones
            remolque = Remolque(id_remolque=contenedorId, fecha_salida=fechaSalida, origen=origen, contenido=productosContenido, rental=True)

            remolques.append(remolque) if remolque else None

        modelo = mainModel(ordenes, remolques)
        # Guarda la predicción usando el servicio
        # prediction_id = prediction_service.savePrediction(
        #     input_data, prediction_response)
        return Response(
            response=json.dumps(
                {"message": "Predicción guardada", "prediction_id": "prediction_id"}),
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
