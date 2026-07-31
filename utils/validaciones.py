from datetime import datetime


def validar_cultivo(nombre: str, area_texto: str, ubicacion: str):
    """
    Valida los datos de un cultivo antes de guardarlo.
    Devuelve una tupla (es_valido: bool, mensaje_error: str, area_num: float|None)
    """
    nombre = nombre.strip()
    ubicacion = ubicacion.strip()

    if not nombre:
        return False, "El nombre del cultivo es obligatorio.", None

    if not ubicacion:
        return False, "La ubicación es obligatoria.", None

    try:
        area_num = float(area_texto)
    except ValueError:
        return False, "El área debe ser un número (ej: 5.5).", None

    if area_num <= 0:
        return False, "El área debe ser mayor a 0.", None

    return True, "", area_num


def validar_fecha(fecha_texto: str):
    """Valida que la fecha tenga formato AAAA-MM-DD y sea una fecha real."""
    try:
        datetime.strptime(fecha_texto, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "La fecha debe tener formato AAAA-MM-DD (ej: 2026-07-31)."


def validar_monitoreo(id_cultivo, fecha_texto, ruta_video, ruta_gps):
    """
    Valida todos los datos de un monitoreo antes de guardarlo.
    Devuelve (es_valido: bool, mensaje_error: str)
    """
    if id_cultivo is None:
        return False, "Debes seleccionar un cultivo."

    valido_fecha, error_fecha = validar_fecha(fecha_texto)
    if not valido_fecha:
        return False, error_fecha

    if not ruta_video:
        return False, "Debes cargar un video térmico (.MP4)."

    if not ruta_video.lower().endswith(".mp4"):
        return False, "El archivo de video debe tener extensión .MP4."

    if ruta_gps and not ruta_gps.lower().endswith(".srt"):
        return False, "El archivo de GPS debe tener extensión .SRT."

    return True, ""