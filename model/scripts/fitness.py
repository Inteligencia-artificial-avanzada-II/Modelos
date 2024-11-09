from collections import defaultdict

def fitness(individuo, ordenes, productos_urgentes):
    # Filtrar solo las órdenes con status "Created" o "Partly Allocated"
    ordenes_creadas = [orden for orden in ordenes if orden.status == "Created" or orden.status == "Partly Allocated"]
    
    # Crear un diccionario con la necesidad total de cada producto de las órdenes creadas
    necesidad_productos = defaultdict(int)
    for orden in ordenes_creadas:
        for producto_info in orden.productos:
            for producto, cantidades in producto_info.items():
                necesidad_productos[producto] += cantidades[1]  # 'solicitada'

    # Calcular el puntaje total del individuo basado en los objetivos
    puntaje_total = 0
    for posicion, remolque in enumerate(individuo):
        # Calcula la contribución del remolque según los productos que contiene
        contribucion_remolque = sum(
            min(int(item['requestedQuantity']), necesidad_productos[item['itemDescription']])
            for item in remolque.contenido
            if item['itemDescription'] in necesidad_productos
        )
        
        # Incremento de peso para remolques cuyo origen es "ATL"
        if remolque.origen == 'ATL':
            contribucion_remolque *= 1.3  # Incremento del 30% para remolques de ATL

        # Ponderación adicional para remolques `rental`
        if remolque.rental:
            contribucion_remolque *= 1.2  # Incremento del 20% por ser rental
            
        # Puntaje adicional si el remolque contiene productos urgentes
        if productos_urgentes:
            contribucion_remolque += sum(
                int(item['requestedQuantity'])
                for item in remolque.contenido
                if item['itemDescription'] in productos_urgentes
            )
        
        # Dar más peso a los remolques al inicio de la lista (posición inversa)
        peso = len(individuo) - posicion  # El primer remolque tiene el mayor peso
        puntaje_total += contribucion_remolque * peso

    return puntaje_total
