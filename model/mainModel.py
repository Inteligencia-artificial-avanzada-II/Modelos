from model.scripts.estrategia_evolutiva import evolve
from model.objects.patio import Patio
from model.objects.cedis import CEDIS
from model.utils.delete_cache import delete_pycache
from model.utils.response import get_response
from model.utils.load_data_as_objects import cargar_ordenes
from model.utils.process_input_xlsx import process_data
from model.utils.install_requirements import install_requirements
install_requirements()


def main(ordenes, remolques):
    errors = {}

    # # Step 1: Procesar el archivo de entrada
    # try:
    #     process_data(f'{rutaArchivo}')
    # except Exception as e:
    #     errors["input_data"] = "Error al procesar los datos de entrada: " + \
    #         str(e)
    #     print(errors)
    #     return get_response(errors)

    # Step 1: Cargar datos y crear los objetos
    try:
        # Consultamoos a fosas y obtenemos la fecha de hoy y todos los camiones en true
        # Hacemos un .split('-') y obtener el primer valor
        # Buscar en las ordenes que estén activas, el id del contenedor
        # Y generar una lista de objetos de camiones
        camiones = orderDict

        # Lectura de archivo Excel
        ordenes = cargar_ordenes(rutaArchivoOrdenes)
    except Exception as e:
        errors["data_load"] = "Error al cargar los datos: " + str(e)
        print(errors)
        return get_response(e)

    # Step 3: Estrategia evolutiva
    # _flag -> mejor fitness de cada flag, en caso de necesitarse en el futuro

    results = {}

    flag = 'DEMANDA'
    try:
        mejor_orden_demanda, _demanda, gens_demanda = evolve(
            flag, camiones, ordenes, cedis)
        result_demanda = [camion.id_camion for camion in mejor_orden_demanda]
        results["propuesta_demanda"] = result_demanda
        print("PROPUESTA GENERADA.")
    except Exception as e:
        errors["propuesta_demanda"] = "Error al generar propuesta DEMANDA: " + \
            str(e)
        print("Error al generar propuesta DEMANDA:\n", e)

    # ------------------------------------------------------------------------------------------------

    flag = "FP"
    try:
        mejor_orden_FP, _FP, gens_FP = evolve(flag, camiones, ordenes, cedis)
        result_FP = [camion.id_camion for camion in mejor_orden_FP]
        results["propuesta_FP"] = result_FP
        print("PROPUESTA GENERADA.")
    except Exception as e:
        errors["propuesta_FP"] = "Error al generar propuesta FP: " + str(e)
        print("Error al generar propuesta FP:\n", e)

    # ------------------------------------------------------------------------------------------------

    flag = "PK"
    try:
        mejor_orden_PK, _PK, gens_PK = evolve(flag, camiones, ordenes, cedis)
        result_PK = [camion.id_camion for camion in mejor_orden_PK]
        results["propuesta_PK"] = result_PK
        print("PROPUESTA GENERADA.")
    except Exception as e:
        errors["propuesta_PK"] = "Error al generar propuesta PK: " + str(e)
        print("Error al generar propuesta PK:\n", e)

    # ------------------------------------------------------------------------------------------------

    flag = "CARGA"
    try:
        mejor_orden_carga, _carga, gens_carga = evolve(
            flag, camiones, ordenes, cedis)
        result_carga = [camion.id_camion for camion in mejor_orden_carga]
        results["propuesta_carga"] = result_carga
        print("PROPUESTA GENERADA.")
    except Exception as e:
        errors["propuesta_carga"] = "Error al generar propuesta CARGA: " + \
            str(e)
        print("Error al generar propuesta CARGA:\n", e)

    delete_pycache()
    return get_response(e=errors, propuestas=results)


if __name__ == "__main__":
    main()
