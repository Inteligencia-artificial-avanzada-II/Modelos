class Orden:
    def __init__(self, id_orden, productos, tipo_de_orden, status):
        self.id_orden = id_orden
        self.productos = productos  # Lista de diccionarios con {producto: [cantidad original, cantidad solicitada, cantidad asignada]}
        self.tipo_de_orden = tipo_de_orden
        self.status = status
        print('Orden inicializada:',self.id_orden)