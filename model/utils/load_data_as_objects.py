import requests
import csv
from io import StringIO
from collections import defaultdict
from model.objects.remolques import Remolque
from model.objects.ordenes import Orden


def cargar_ordenes(archivo_url):
    # Obtener el contenido del archivo desde la URL
    response = requests.get(archivo_url)
    response.raise_for_status()  # Lanza una excepción si hay un error en la descarga

    ordenes_dict = defaultdict(
        lambda: {'tipo_de_orden': None, 'status': None, 'productos': defaultdict(list)})

    # Leer el contenido como CSV desde el texto descargado
    csvfile = StringIO(response.text)
    reader = csv.DictReader(csvfile)

    for row in reader:
        id_orden = row['id_orden']
        producto = row['producto']
        tipo_de_orden = row['tipo_de_orden']
        status = row['status']
        original = int(row['original'])
        solicitada = int(row['solicitada'])
        asignada = int(row['asignada'])

        # Si no tiene tipo_de_orden y status, se guardan en la primera instancia
        if ordenes_dict[id_orden]['tipo_de_orden'] is None:
            ordenes_dict[id_orden]['tipo_de_orden'] = tipo_de_orden
            ordenes_dict[id_orden]['status'] = status

        # Agregar el producto y sus cantidades
        ordenes_dict[id_orden]['productos'][producto] = [
            original, solicitada, asignada]

    # Convertir el diccionario a una lista de instancias de Orden
    ordenes = [
        Orden(
            id_orden=id_orden,
            tipo_de_orden=info['tipo_de_orden'],
            status=info['status'],
            productos=[{producto: cantidades}
                        for producto, cantidades in info['productos'].items()]
        )
        for id_orden, info in ordenes_dict.items()
    ]

    print('Órdenes cargadas con éxito.')

    return ordenes
