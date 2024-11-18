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


@mongoPredictionsBp.route("/test", methods=['GET'])
def testConnection():
    return Response(response=json.dumps(
        {"Message": "OK"}),
        status=200,
        mimetype="application/json")


@mongoPredictionsBp.route("/predict", methods=["POST"])
def savePrediction():
    remolques = []
    ordenes = cargar_ordenes(Config.RUTA_ARCHIVO_ORDENES)
    products = []
    data = request.json
    if not data:
        return Response(
            response=json.dumps(
                {"message": "El cuerpo de la solicitud está vacío o no es JSON válido.", "data": {}}),
            status=400,
            mimetype="application/json"
        )
    else:
        dataDict = json.loads(json.dumps(data))

    headersToken = request.headers.get('Authorization')
    token = headersToken.split('Token ')[1]

    headersForSent = {
        'Content-Type': 'application/json',
        "Authorization": f"Token {token}"
    }

    print(headersForSent)

    # Validación de datos de entrada
    extraData = dataDict.get("extraData")
    print(extraData)

    try:
        apiOrdenContenedorId = f'{Config.RUTA_BACK}/orden/consultarQrUrl'
        apiFosasGetAll = f'{Config.RUTA_BACK}/fosa/consultarTodos'
        apiOrdenMongoId = f'{Config.RUTA_BACK}/ordenmongo/consultar'
        apiListaCrearPrioridadModelo = f'{
            Config.RUTA_BACK}/listaprioridadcontenedor/crear'
        apiConsultarContenedorId = f'{Config.RUTA_BACK}/contenedor/consultar'
        apiPrioridadProductoAll = f'{
            Config.RUTA_BACK}/priorityproduct/consultarTodos'
        print("Rutas declaradas")
        responseFosas = requests.get(apiFosasGetAll, headers=headersForSent)
        print(responseFosas)
        dataFosas = json.loads(json.dumps(responseFosas.json()))
        fosa = dataFosas[0]
        dailyFosa = fosa['fosa']['daily']
        fechaNow = "18/11/24"  # datetime.now().strftime("%d/%m/%Y")
        dailyFechaData = dailyFosa.get(fechaNow)

        if not dailyFechaData:
            return Response(
                response=json.dumps(
                    {"message": "No se encontraron remolques en fosas el día de hoy", "data": {}}),
                status=400,
                mimetype="application/json"
            )

        for dailyFechaKey, dailyFechaValue in dailyFechaData.items():

            if not dailyFechaValue:
                continue

            contenedorId = dailyFechaKey.split(
                '-')[0] if dailyFechaKey else None

            try:
                responseOrdenData = requests.get(
                    f'{apiOrdenContenedorId}/{contenedorId}', headers=headersForSent) if contenedorId else None
            except Exception as e:
                return Response(
                    response=json.dumps(
                        {"message": f"No se encontraron remolques por ordenar {e}", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )

            try:
                responseContenedorId = requests.get(
                    f'{apiConsultarContenedorId}/{contenedorId}', headers=headersForSent) if contenedorId else None
            except Exception as e:
                return Response(
                    response=json.dumps(
                        {"message": f"No se encontraron remolques por ordenar {e}", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )

            if responseOrdenData.status_code != 200 != responseContenedorId.status_code:
                return Response(
                    response=json.dumps(
                        {"message": "Lo sentimos, no se encontró el contenedor o una orden relacionada al contenedor", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )

            dataContenedorId = responseContenedorId.json()

            rentalContenedor = dataContenedorId.get('rental', False)

            ordenSqlData = responseOrdenData.json(
            )['data'] if responseOrdenData else None

            if not ordenSqlData:
                return Response(
                    response=json.dumps(
                        {"message": "No se encontraron órdenes relacionadas al remolque el día de hoy", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )
            ordenMongoId = ordenSqlData.get(
                'idMongoProductos') if ordenSqlData else None
            responseOrdenMongoData = requests.get(
                f'{apiOrdenMongoId}/{ordenMongoId}', headers=headersForSent) if ordenMongoId else None
            ordenMongoData = responseOrdenMongoData.json().get(
                'data') if responseOrdenMongoData else None
            origen = ordenSqlData.get('origen') if ordenSqlData else None
            fechaSalida = ordenMongoData.get(
                'fechaSalida') if ordenMongoData else None
            productosContenido = ordenMongoData.get(
                'products') if ordenMongoData else None

            for productoContenido in productosContenido:
                productoContenido['requestedQuantity'] = int(
                    productoContenido['requestedQuantity']) if productoContenido.get('requestedQuantity') else 0
                productoContenido['salePrice'] = float(productoContenido['salePrice']) if productoContenido.get(
                    'salePrice') else productoContenido['salePrice']

            # Creamos la lista de los camiones
            remolque = Remolque(id_remolque=contenedorId, fecha_salida=fechaSalida,
                                origen=origen, contenido=productosContenido, rental=rentalContenedor)

            remolques.append(remolque if remolque else None)
            set(remolques)
            print(remolques)

        # Obtenemos productos prioritarios
        responsePrioritarios = requests.get(
            apiPrioridadProductoAll, headers=headersForSent)
        prioritariosData = responsePrioritarios.json().get(
            'data')[0] if responsePrioritarios.status_code == 200 else None
        productsList = prioritariosData.get('products')

        for productList in productsList:
            products.append(productList.get('descripcion'))

        if not remolques:
            return Response(
                response=json.dumps(
                    {"message": "No se encontraron remolques por ordenar", "data": {}}),
                status=400,
                mimetype="application/json"
            )

        if len(remolques) == 1:
            respuestModelo = [remolques[0].id_remolque]
        else:
            modelo = model(remolques, ordenes, products)
            respuestModelo = modelo.get('propuesta')

        dataForListaPrioridad = {
            "contenedores": respuestModelo
        }

        requests.post(apiListaCrearPrioridadModelo,
                      dataForListaPrioridad, headers=headersForSent)

        # Guarda la predicción usando el servicio
        # prediction_id = prediction_service.savePrediction(
        #     input_data, prediction_response)
        return Response(
            response=json.dumps(
                {"message": "Prediccion realizada exitosamente", "data": respuestModelo}),
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
