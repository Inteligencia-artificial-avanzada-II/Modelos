from utils.install_requirements import install_requirements
install_requirements()
from utils.response import get_response
from utils.delete_cache import delete_pycache
from scripts.estrategia_evolutiva import evolve

def model(remolques,ordenes,productos_urgentes):
    errors = None
    result = []
    
    # Estrategia evolutiva

    try:
        delete_pycache()
        mejor_orden, mejor_puntaje, generacion_max = evolve(remolques, ordenes, productos_urgentes)
        result = [remolque.id_remolque for remolque in mejor_orden]
        print("PROPUESTA GENERADA.")
    except Exception as e:
        errors = "Error al generar propuesta : " + str(e)
        print("Error al generar propuesta :\n", e)

    return get_response(e=errors,propuesta=result)