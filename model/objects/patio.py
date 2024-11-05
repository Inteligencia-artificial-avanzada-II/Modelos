class Patio:
    def __init__(self):
        # Lista de camiones esperando en el patio
        self.camion = None
        print('Patio inicializado.')
    
    def agregar_camion(self, camion):
        """
        Agrega un camión a la lista de espera del patio.
        """
        self.camion.append(camion)
        camion.status = "esperando"
        print(f"Camión {camion.id_camion} agregado a la zona de espera.")
    
    def remover_camion(self, camion):
        """
        Remueve un camión de la lista de espera del patio.
        """
        if camion == self.camion:
            self.camion = None
            print(f"Camión {camion.id_camion} removido de la zona de espera.")
    
    def asignar_camion_a_fosa(self, fosa):
        """
        Asignar el camion a una fosa
        """
        if not self.camion:
            print("No hay camiones en espera.")
            return

        # Asignar el camion a una Fosa
        if fosa.estado == 'libre':
            # Asignar el primer camión en espera a la fosa
            camion = self.camion = None
            fosa.asignar_camion(camion)
            print(f"Camión {camion.id_camion} asignado a la {fosa.id_fosa}.")
            return

        print("La fosa no está libre")