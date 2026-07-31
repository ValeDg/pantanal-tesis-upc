import shutil
import os

CARPETA_DESTINO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "archivos_cargados")


def copiar_archivo(ruta_origen: str) -> str:
    """
    Copia el archivo seleccionado por el usuario hacia archivos_cargados/,
    para que el proyecto no dependa de que el archivo original siga
    en su ubicación original (ej: una USB que se puede desconectar).
    Devuelve la nueva ruta dentro del proyecto.
    """
    os.makedirs(CARPETA_DESTINO, exist_ok=True)
    nombre_archivo = os.path.basename(ruta_origen)
    ruta_destino = os.path.join(CARPETA_DESTINO, nombre_archivo)
    shutil.copy2(ruta_origen, ruta_destino)
    return ruta_destino