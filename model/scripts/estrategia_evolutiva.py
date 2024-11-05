import random
from scripts.fitness import producto_demandado, producto_demandado_FP, producto_demandado_PK, menor_producto, producto_escaso

# Función de evaluación de la solución según la flag
def fitness(individuo, ordenes, flag):
    if flag == "DEMANDA":
        return producto_demandado(individuo, ordenes)
    elif flag == "FP":
        return producto_demandado_FP(individuo,ordenes)
    elif flag == "PK":
        return producto_demandado_PK(individuo, ordenes)
    elif flag == "CARGA":
        return menor_producto(individuo)
    else:
        raise ValueError("Flag no reconocida. Use 'DEMANDA', 'ESCASEZ' o 'CARGA'.")

# Función de mutación para crear variantes del mejor individuo
def mutacion(individuo, probs):
    # Realizar pequeñas modificaciones en el orden de camiones
    probabilidad = random.random()
    
    if probabilidad < probs:
        # 50% de las veces: Intercambio de dos posiciones aleatorias
        idx1, idx2 = random.sample(range(len(individuo)), 2)
        individuo[idx1], individuo[idx2] = individuo[idx2], individuo[idx1]
    else:
        # 50% de las veces: Insertar un camión en una posición aleatoria
        idx1 = random.randint(0, len(individuo) - 1)
        idx2 = random.randint(0, len(individuo) - 1)
        camion = individuo.pop(idx1)
        individuo.insert(idx2, camion)
    
    return individuo

# Estrategia evolutiva con mejora continua
def evolve(flag, camiones, ordenes, tamano_poblacion=30, num_generaciones=20, probs=0.5):
    # Generar un individuo inicial como el mejor hasta ahora
    mejor_individuo = random.sample(camiones, len(camiones))
    mejor_puntaje = fitness(mejor_individuo, ordenes, flag)
    generacion_max = 0  # Registrar la generación en la que se alcanza el mejor puntaje TEMPORAL

    for generacion in range(num_generaciones):
        print(f"\n--- Generación {generacion + 1} ---")
        
        # Crear una nueva población a partir de mutaciones del mejor individuo
        nueva_poblacion = [mutacion(list(mejor_individuo),probs) for _ in range(tamano_poblacion)]
        
        # Evaluar la nueva población para encontrar el mejor individuo
        mejor_individuo_generacion = max(nueva_poblacion, key=lambda ind: fitness(ind, ordenes, flag))
        mejor_puntaje_generacion = fitness(mejor_individuo_generacion, ordenes, flag)
        
        # Comparar el mejor de esta generación con el mejor global
        if mejor_puntaje_generacion > mejor_puntaje:
            mejor_individuo = mejor_individuo_generacion
            mejor_puntaje = mejor_puntaje_generacion
            generacion_max = generacion + 1  # Actualizar la generación en la que se alcanzó el mejor puntaje TEMPORAL
        
        # Imprimir el puntaje del mejor individuo en esta generación
        print(f"Mejor puntaje de la generación {generacion + 1}: {mejor_puntaje}")
        print("Mejor individuo (orden de camiones):", [camion.id_camion for camion in mejor_individuo])

    print('-'*50)

    # Retornar el mejor orden final, el mejor puntaje y la generación en la que se alcanzó
    # mejor_puntaje y generacion_max son temporales. se usan para analizar la experimentación
    return mejor_individuo, mejor_puntaje, generacion_max