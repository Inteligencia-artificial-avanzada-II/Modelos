class Camion:
    def __init__(self, id_camion, fecha_salida, origen, contenido):
        self.id_camion = id_camion
        self.fecha_salida = fecha_salida
        self.origen = origen
        self.contenido = contenido  # Lista de diccionarios con {producto: cantidad}
        self.status = "esperando"
        print('Camión inicializado:',self.id_camion)