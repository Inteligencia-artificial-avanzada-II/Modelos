from flask import Blueprint, request, Response
import requests
from datetime import datetime
import json
from managers.mongoPredictionsServices import PredictionService
from model.objects.remolques import Remolque
from model.utils.load_data_as_objects import cargar_ordenes
from model.model import model

from config import Config

mongoPredictionsBp = Blueprint("mongoPredictionsBp", __name__)
prediction_service = PredictionService()


@mongoPredictionsBp.route("/predict", methods=["POST"])
def savePrediction():
    remolques = []
    print("RUTA", f'{Config.RUTA_ARCHIVO_ORDENES}')
    ordenes = cargar_ordenes(f'https://objectstorage.mx-queretaro-1.oraclecloud.com/p/79AJJfgFXexqbvQZWz9MJ_7qJ9xLb94V9XhEAGlRZJbwkfxL1F7gZP9EOHseYtm8/n/axnhu2vnql31/b/qrprueba/o/LibroOrdenes.csv')
    products = []
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
        apiPrioridadProductoAll = f'{Config.RUTA_BACK}/priorityproduct/consultarTodos'
        responseFosas = requests.get(apiFosasGetAll)
        dataFosas = json.loads(json.dumps(responseFosas.json()))
        allFosas = dataFosas[0]['fosas']

        for fosa in allFosas:
            dailyFosa = fosa['daily']
            fechaNow = '10/10/24'#datetime.now().strftime("%d/%m/%Y")

            dailyFechaData = dailyFosa.get(fechaNow)
            contenedorIdKey = next(iter(dailyFechaData.keys())) if dailyFechaData else None
            contenedorId = contenedorIdKey.split('-')[0] if contenedorIdKey else None

            responseOrdenData = requests.get(f'{apiOrdenContenedorId}/{contenedorId}', headers=headersForSent) if contenedorId else None

            ordenSqlData = responseOrdenData.json()['data'] if responseOrdenData else None

            if not ordenSqlData:
                continue
            ordenMongoId = ordenSqlData.get('idMongoProductos') if ordenSqlData else None
            responseOrdenMongoData = requests.get(f'{apiOrdenMongoId}/{ordenMongoId}', headers=headersForSent) if ordenMongoId else None
            ordenMongoData = responseOrdenMongoData.json().get('data') if responseOrdenMongoData else None
            origen = ordenSqlData.get('origen') if ordenSqlData else None
            fechaSalida = ordenMongoData.get('fechaSalida') if ordenMongoData else None
            productosContenido = ordenMongoData.get('products') if ordenMongoData else None

            for productoContenido in productosContenido:
                productoContenido['requestedQuantity'] = int(productoContenido['requestedQuantity']) if productoContenido.get('requestedQuantity') else 0
                productoContenido['salePrice'] = float(productoContenido['salePrice']) if productoContenido.get('salePrice') else productoContenido['salePrice']

                print(productoContenido)

            # Creamos la lista de los camiones
            remolque = Remolque(id_remolque=contenedorId, fecha_salida=fechaSalida, origen=origen, contenido=productosContenido, rental=True)

            remolques.append(remolque if remolque else None)

        # Obtenemos productos prioritarios
        responsePrioritarios = requests.get(apiPrioridadProductoAll, headers=headersForSent)
        prioritariosData = responsePrioritarios.json().get('data')[0] if responsePrioritarios.status_code == 200 else None
        productsList = prioritariosData.get('products')

        for productList in productsList:
            products.append(productList.get('itemDescription'))

        modelo = model(remolques, ordenes, products)
        respuestModelo = modelo.get('propuesta')
        # Guarda la predicción usando el servicio
        # prediction_id = prediction_service.savePrediction(
        #     input_data, prediction_response)
        return Response(
            response=json.dumps(
                {"message": "Prediccion realizada y guardada exitosamente", "data": respuestModelo}),
            status=201,
            mimetype="application/json"
        )
    except Exception as e:
        # Manejo de errores en caso de fallo
        return Response(
            response=json.dumps(
                {"message": f"Ocurrió un error al guardar la predicción: {str(e)}", "data": {}}),
            status=500,
            mimetype="application/json"
        )
