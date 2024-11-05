class Patio:
    def __init__(self):
        # Lista de camiones esperando en el patio
        self.camiones_en_espera = []
        print('Patio inicializado.')
    
    def agregar_camion(self, camion):
        """
        Agrega un camión a la lista de espera del patio.
        """
        self.camiones_en_espera.append(camion)
        camion.status = "esperando"
        print(f"Camión {camion.id_camion} agregado a la zona de espera.")
    
    def remover_camion(self, camion):
        """
        Remueve un camión de la lista de espera del patio.
        """
        if camion in self.camiones_en_espera:
            self.camiones_en_espera.remove(camion)
            print(f"Camión {camion.id_camion} removido de la zona de espera.")
    
    def mostrar_camiones_en_espera(self):
        """
        Muestra los camiones actualmente en espera en el patio.
        """
        print("Camiones en espera en el patio:")
        for camion in self.camiones_en_espera:
            print(f"- Camión {camion.id_camion}:  Estado: {camion.status}, Contenido: {camion.contenido}")
    
    def asignar_camion_a_fosa(self, cedis):
        """
        Asigna el primer camión en la lista de espera a una fosa disponible en el CEDIS.
        """
        if not self.camiones_en_espera:
            print("No hay camiones en espera.")
            return

        # Buscar una fosa libre en el CEDIS
        for fosa in cedis.fosas:
            if fosa.estado == 'libre':
                # Asignar el primer camión en espera a la fosa
                camion = self.camiones_en_espera.pop(0)
                fosa.asignar_camion(camion)
                print(f"Camión {camion.id_camion} asignado a la {fosa.id_fosa}.")
                return

        print("No hay fosas disponibles en el CEDIS. Camión en espera.")