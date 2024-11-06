class Remolque:
    def __init__(self, id_remolque, fecha_salida, origen, contenido, rental):
        self.id_remolque = id_remolque
        self.fecha_salida = fecha_salida
        self.origen = origen
        self.contenido = contenido
        self.rental = rental
        print('Camión inicializado:',self.id_remolque)