def validar_cultivo(nombre: str, area_texto: str, ubicacion: str):
    """
    Valida los datos de un cultivo antes de guardarlo.
    Devuelve una tupla (es_valido: bool, mensaje_error: str, area_num: float|None)
    """
    nombre = nombre.strip()      # quita espacios en blanco al inicio/final
    ubicacion = ubicacion.strip()

    if not nombre:
        return False, "El nombre del cultivo es obligatorio!!", None

    if not ubicacion:
        return False, "La ubicación es obligatoria!!", None

    # El usuario escribe el área como texto en el Entry; intentamos convertirlo
    try:
        area_num = float(area_texto)
    except ValueError:
        return False, "El área debe ser un número (ejem: 5.5).", None

    if area_num <= 0:
        return False, "El área debe ser mayor a 0.", None

    return True, "", area_num