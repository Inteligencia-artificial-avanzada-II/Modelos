# Importación de librerías
from flask import Blueprint, request, Response
import requests
from datetime import datetime
import pytz
import json

# Importación de funciones u objetos
from managers.mongoPredictionsServices import PredictionService
from model.objects.remolques import Remolque
from model.utils.load_data_as_objects import cargar_ordenes
from model.model import model

# Importamos  nuestra configuración
from config import Config

# Configuración del blueprint y el servicio de predicción
mongoPredictionsBp = Blueprint("mongoPredictionsBp", __name__)
prediction_service = PredictionService()


# Función para probar la conexión al controlador
@mongoPredictionsBp.route("/test", methods=['GET'])
def testConnection():
    return Response(response=json.dumps(
        {"Message": "OK"}),
        status=200,
        mimetype="application/json")

# Función para manejar la predicción y guardar resultados
@mongoPredictionsBp.route("/predict", methods=["POST"])
def savePrediction():
    remolques = [] # Lista de remolques procesados
    listaValidacion = [] # Lista para validar remolques y validar repetidos
    ordenes = cargar_ordenes(Config.RUTA_ARCHIVO_ORDENES) # Cargamos las órdenes y las procesamos para convertirla en lista
    products = [] # Lista donde se guardarán productos prioritarios

    # Validación para el cuerpo de la solicitud
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

    # Obtención del token del encabezado de autorización
    headersToken = request.headers.get('Authorization')
    token = headersToken.split('Token ')[1]

    headersForSent = {
        'Content-Type': 'application/json',
        "Authorization": f"Token {token}"
    }

    # Validación de datos de entrada
    extraData = dataDict.get("extraData")

    try:
        # Configuramos nuestras rutas y las añadimos en variables
        apiOrdenContenedorId = f'{Config.RUTA_BACK}/orden/consultarQrUrl'
        apiFosasGetAll = f'{Config.RUTA_BACK}/fosa/consultarTodos'
        apiOrdenMongoId = f'{Config.RUTA_BACK}/ordenmongo/consultar'
        apiListaCrearPrioridadModelo = f'{
            Config.RUTA_BACK}/listaprioridadcontenedor/crear'
        apiConsultarContenedorId = f'{Config.RUTA_BACK}/contenedor/consultar'
        apiPrioridadProductoAll = f'{
            Config.RUTA_BACK}/priorityproduct/consultarTodos'

        # Realizamos la petición para obtener las fosas donde se guardan los camiones en el patio
        responseFosas = requests.get(apiFosasGetAll, headers=headersForSent)

        # Procesamos el json que recibimos de la petición para poder acceder a él
        dataFosas = json.loads(json.dumps(responseFosas.json()))
        fosa = dataFosas[0] # Accedemos al primer valor, ya que nos devuelve una lista de objetos
        dailyFosa = fosa['fosa']['daily'] # Accedemos a la profundidad "daily" de la fosa
        # Zona horaria de México
        mexicoTimeZone = pytz.timezone('America/Mexico_City')
        # Obtener la fecha actual en la zona horaria de México
        fechaNow = datetime.now(mexicoTimeZone).strftime("%d/%m/%y")
        # Obtenemos la fecha del día de hoy en nuestro diccionario "daily"
        dailyFechaData = dailyFosa.get(fechaNow)

        # Validamos que daily contenga datos
        if not dailyFechaData:
            return Response(
                response=json.dumps(
                    {"message": f"No se encontraron remolques en fosas el día de hoy {dailyFechaData}", "data": {}}),
                status=400,
                mimetype="application/json"
            )

        # Recorremos nuestro diccionario de la fecha de hoy si es que hay datos
        for dailyFechaKey, dailyFechaValue in dailyFechaData.items():

            # Si el valor es False o no tiene nada, continuamos a la siguiente iteración
            if not dailyFechaValue:
                continue

            # Obtenemos el contenedorId en caso de que exista, si no hay valor se queda None por defecto
            contenedorId = dailyFechaKey.split(
                '-')[0] if dailyFechaKey else None

            # Validamos si el contenedor ya se encuentra en listaValidación, si es así pasamos a la siguiente iteración para evitar repetidos
            if contenedorId in listaValidacion:
                continue 

            try:
                # Realizamos petición para obtener la orden relacionada a ese contenedor
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
                # Realizamos la petición para obtener os datos del contenedor
                responseContenedorId = requests.get(
                    f'{apiConsultarContenedorId}/{contenedorId}', headers=headersForSent) if contenedorId else None
            except Exception as e:
                return Response(
                    response=json.dumps(
                        {"message": f"No se encontraron remolques por ordenar {e}", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )

            # Validamos que las peticiones anteriores hayan sido exitosas
            if (responseOrdenData.status_code != 200) or (responseContenedorId.status_code != 200):
                return Response(
                    response=json.dumps(
                        {"message": "Lo sentimos, no se encontró el contenedor o una orden relacionada al contenedor", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )

            # Pasamos a json la respuesta de la petición de la información del contenedor
            dataContenedorId = responseContenedorId.json()

            # Declaramos la variable para verificar si es un contenedor rentado o no
            rentalContenedor = dataContenedorId.get('rental', False)

            # Obtenemos los datos de la orden en caso de que haya, si no hay orden se ponen None por defecto
            ordenSqlData = responseOrdenData.json(
            )['data'] if responseOrdenData else None

            # Validamos que existan datos en la orden de ese contenedor
            if not ordenSqlData:
                return Response(
                    response=json.dumps(
                        {"message": "No se encontraron órdenes relacionadas al remolque el día de hoy", "data": {}}),
                    status=400,
                    mimetype="application/json"
                )
            # Obtenemos el id de mongo que se encuentra en los detalles de la orden
            ordenMongoId = ordenSqlData.get(
                'idMongoProductos') if ordenSqlData else None
            # Realizamos la petición para obtener la data de Mongo, donde vienen los productos e información extra sobre la orden
            responseOrdenMongoData = requests.get(
                f'{apiOrdenMongoId}/{ordenMongoId}', headers=headersForSent) if ordenMongoId else None
            ordenMongoData = responseOrdenMongoData.json().get(
                'data') if responseOrdenMongoData else None
            # Obtenemos el origen de donde proviene esa orden
            origen = ordenSqlData.get('origen') if ordenSqlData else None
            # Obtenemos la fecha en la que salió dicho contenedor
            fechaSalida = ordenMongoData.get(
                'fechaSalida') if ordenMongoData else None
            # Obtenemos todos los productos que trae el contenedor
            productosContenido = ordenMongoData.get(
                'products') if ordenMongoData else None

            # Recorremos todos los productos y lo procesamos para convertir sus valores númericos a enteros o flotantes y no str
            for productoContenido in productosContenido:
                productoContenido['requestedQuantity'] = int(
                    productoContenido['requestedQuantity']) if productoContenido.get('requestedQuantity') else 0
                productoContenido['salePrice'] = float(productoContenido['salePrice']) if productoContenido.get(
                    'salePrice') else productoContenido['salePrice']

            # Creamos la lista de los camiones
            remolque = Remolque(id_remolque=contenedorId, fecha_salida=fechaSalida,
                                origen=origen, contenido=productosContenido, rental=rentalContenedor)
            # Agregamos los contenedores a nuestra lista de validación y a la lista a enviar
            listaValidacion.append(contenedorId)
            remolques.append(remolque if remolque else None)

        # Obtenemos productos prioritarios
        responsePrioritarios = requests.get(
            apiPrioridadProductoAll, headers=headersForSent)
        prioritariosData = responsePrioritarios.json().get(
            'data')[0] if responsePrioritarios.status_code == 200 else None
        productsList = prioritariosData.get('products') # Obtenemos todos los productos prioritarios

        # Procesamos los productos prioritarios
        for productList in productsList:
            products.append(productList.get('descripcion'))

        # validamos que la lista de remolques contenga datos
        if not remolques:
            return Response(
                response=json.dumps(
                    {"message": "No se encontraron remolques por ordenar", "data": {}}),
                status=400,
                mimetype="application/json"
            )

        # Si la longitud es 1, no tiene caso pasar por la estrategia evolutiva, por lo que devolvemos únicamente el remolque con su id
        if len(remolques) == 1:
            respuestModelo = [remolques[0].id_remolque]
        else:
            # En caso de que sean más de uno, procedemos a mandar a llamar a la estrategia evolutiva
            modelo = model(remolques, ordenes, products)
            # Declaramos la variable y obtenemos la respuesta de la estrategia evolutiva
            respuestModelo = modelo.get('propuesta')

        # Generamos nuestro diccionario para retornar
        dataForListaPrioridad = {
            "contenedores": respuestModelo
        }

        try:
            # Realizamos petición para actualizar nuestra lista de prioridad de contenedores
            requests.post(apiListaCrearPrioridadModelo, data=json.dumps(dataForListaPrioridad), headers=headersForSent)
        except Exception as e:
            return Response(
                response=json.dumps(
                    {"message": f"Lo sentimos, ocurrió un error al actualizar la lista{e}", "data": {}}),
                status=400,
                mimetype="application/json"
            )

        # Si todo sale bien, devolvemos una respuesta de éxito junto con la data preparada anteriormente
        return Response(
            response=json.dumps(
                {"message": "Prediccion realizada exitosamente", "data": respuestModelo}),
            status=201,
            mimetype="application/json"
        )
    # En caso de que haya errores, los manejamos aquí
    except Exception as e:
        # Manejo de errores en caso de fallo
        return Response(
            response=json.dumps(
                {"message": f"Ocurrió un error al guardar la predicción: {str(e)}", "data": {}}),
            status=500,
            mimetype="application/json"
        )
