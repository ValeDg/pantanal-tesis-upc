import shutil
import os

CARPETA_DESTINO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "archivos_cargados")


def copiar_archivo(ruta_origen: str) -> str:
    """
    Copia el archivo seleccionado hacia archivos_cargados/. Si el archivo
    ya está dentro de esa carpeta (mismo archivo), no hace nada y devuelve
    la ruta tal cual, para evitar el error de copiar un archivo sobre sí mismo.
    """
    os.makedirs(CARPETA_DESTINO, exist_ok=True)
    nombre_archivo = os.path.basename(ruta_origen)
    ruta_destino = os.path.join(CARPETA_DESTINO, nombre_archivo)

    # os.path.abspath normaliza ambas rutas para poder compararlas de forma confiable
    if os.path.abspath(ruta_origen) == os.path.abspath(ruta_destino):
        return ruta_origen

    shutil.copy2(ruta_origen, ruta_destino)
    return ruta_destino