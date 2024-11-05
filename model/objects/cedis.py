import pandas as pd

class CEDIS:
    def __init__(self, n_fosas, path_inventario):
        # Crear las fosas con los nombres "Fosa-1", "Fosa-2", ...
        self.fosas = [Fosa(f"Fosa-{i+1}") for i in range(n_fosas)]
        # Leer el inventario como un DataFrame
        self.inventario = pd.read_csv(path_inventario)
        print('CEDIS inicializado con',len(self.fosas),'fosas')
        
    def asignar_camion_a_fosa(self, camion):
        # Buscar una fosa libre y asignarle el camión
        for fosa in self.fosas:
            if fosa.estado == 'libre':
                fosa.asignar_camion(camion)
                return
        print("No hay fosas disponibles en este momento.")

    def liberar_fosa_por_id(self, id_fosa):
        # Encontrar la fosa por su id y liberarla
        for fosa in self.fosas:
            if fosa.id_fosa == id_fosa and fosa.estado == 'ocupada':
                fosa.liberar_fosa()
                return
        print(f"La fosa {id_fosa} ya está libre o no existe.")

# Clase Fosa proporcionada para referencia
class Fosa:
    def __init__(self, id_fosa):
        self.id_fosa = id_fosa
        self.estado = 'libre'
        self.camiones = []

    def asignar_camion(self, camion):
        if self.estado == 'libre' or len(self.camiones) < 3:
            self.camiones.append(camion)
            camion.estado = 'descargando'
            print(f"Fosa {self.id_fosa} asignada a Camión {camion.id_camion}")
            if len(self.camiones) == 3:
                self.estado = 'llena'
        else:
            print(f"Fosa {self.id_fosa} está llena y no puede asignar más camiones.")

    def liberar_camion(self, camion):
        if camion in self.camiones:
            self.camiones.remove(camion)
            camion.estado = 'retirado'
            print(f"Camión {camion.id_camion} liberado de Fosa {self.id_fosa}")
            if not self.camiones:
                self.estado = 'libre'
            elif len(self.camiones) < 3:
                self.estado = 'ocupada'
        else:
            print(f"Camión {camion.id_camion} no está asignado a Fosa {self.id_fosa}")

    def liberar_fosa(self):
        if self.camiones:
            for camion in self.camiones:
                camion.estado = 'retirado'
                print(f"Fosa {self.id_fosa} liberada de Camión {camion.id_camion}")
            self.camiones.clear()
            self.estado = 'libre'