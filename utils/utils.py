def str_to_bool(value):
    """
    * Función para convertir string a booleano

    * Args:
        value (stro): El valor a convertir

    * Returns:
        bool: True si el valor es igual a "true, 1 o yes"
    """
    return value.lower() in ("true", "1", "yes")
