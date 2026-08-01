import cv2


def extraer_fotogramas(ruta_video: str, cada_n_fotogramas: int = 15):
    """
    Abre un video y devuelve una lista de fotogramas muestreados,
    junto con el número real de fotograma al que corresponde cada uno.

    cada_n_fotogramas=15 significa: nos quedamos con 1 de cada 15
    (a ~30fps, esto es aproximadamente 1 fotograma cada medio segundo).

    Devuelve: lista de tuplas (numero_fotograma, imagen)
    """
    captura = cv2.VideoCapture(ruta_video)

    if not captura.isOpened():
# El archivo existe pero OpenCV no pudo abrirlo (corrupto, formato no soportado, etc.) MENSAJE DE ERROR
        raise ValueError(f"No se pudo abrir el video: {ruta_video}")

    fotogramas_muestreados = []
    numero_fotograma = 0

    while True:
        exito, imagen = captura.read()  # esto va a leer el siguiente fotograma

        if not exito:
# exito=False significa que ya no hay más fotogramas (se acabó el video)
            break

# Solo nse queda con 1 de cada N, para no procesar miles de imágenes casi iguales
        if numero_fotograma % cada_n_fotogramas == 0:
            fotogramas_muestreados.append((numero_fotograma, imagen))

        numero_fotograma += 1

    captura.release()  # se libera el archivo, igual que cerramos una conexión SQLite

    return fotogramas_muestreados