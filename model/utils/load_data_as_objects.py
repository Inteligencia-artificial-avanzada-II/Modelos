import csv
from collections import defaultdict
from objects.camiones import Camion
from objects.ordenes import Orden

def cargar_camiones(archivo_csv):
    camiones_dict = defaultdict(lambda: {'fecha_salida': None, 'origen': None, 'contenido': defaultdict(int)})
    
    with open(archivo_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id_camion = row['id_camion']
            producto = row['producto']
            cantidad = int(row['cantidad'])
            
            # Si no tiene fecha_salida y origen, se guardan en la primera instancia
            if camiones_dict[id_camion]['fecha_salida'] is None:
                camiones_dict[id_camion]['fecha_salida'] = row['fecha_salida']
                camiones_dict[id_camion]['origen'] = row['origen']
            
            # Acumular cantidades de productos
            camiones_dict[id_camion]['contenido'][producto] += cantidad 
    
    # Convertir el diccionario a una lista de instancias de Camion
    camiones = [
        Camion(
            id_camion=id_camion,
            fecha_salida=info['fecha_salida'],
            origen=info['origen'],
            contenido=[{producto: cantidad} for producto, cantidad in info['contenido'].items()]
        )
        for id_camion, info in camiones_dict.items()
    ]

    print('camiones creados con éxito.')
    
    return camiones

def cargar_ordenes(archivo_csv):
    ordenes_dict = defaultdict(lambda: {'tipo_de_orden': None, 'status': None, 'productos': defaultdict(list)})
    
    with open(archivo_csv, newline='') as csvfile:
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
            ordenes_dict[id_orden]['productos'][producto] = [original, solicitada, asignada]
    
    # Convertir el diccionario a una lista de instancias de Orden
    ordenes = [
        Orden(
            id_orden=id_orden,
            tipo_de_orden=info['tipo_de_orden'],
            status=info['status'],
            productos=[{producto: cantidades} for producto, cantidades in info['productos'].items()]
        )
        for id_orden, info in ordenes_dict.items()
    ]

    print('ordenes cargadas con éxito.')
    
    return ordenes