import re

def parsear_srt(ruta_srt: str) -> dict:
    """
    Lee un archivo .SRT de telemetría de dron y devuelve un diccionario:
    { numero_bloque: {"latitud": float, "longitud": float}, ... }

    Si un bloque no tiene coordenadas válidas, se omite (no se agrega al diccionario).
    """
    with open(ruta_srt, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

# Los bloques de un .SRT están separados por una línea en blanco.    
# Dividimos el archivo completo en esos bloques individuales.
  
    bloques_texto = contenido.strip().split("\n\n")

    coordenadas_por_bloque = {}

    for bloque in bloques_texto:
        # La primera línea de cada bloque es el número de bloque (1, 2, 3...)
        lineas = bloque.strip().split("\n")
        if not lineas:
            continue

        try:
            numero_bloque = int(lineas[0].strip())
        except ValueError:
            continue  # si la primera línea no es un número, este bloque no tiene el formato esperado

        # Buscamos latitude y longitude en TODO el texto del bloque (pueden estar en cualquier línea)
        match_lat = re.search(r"latitude:\s*(-?\d+\.\d+)", bloque)
        match_lon = re.search(r"longitude:\s*(-?\d+\.\d+)", bloque)

        if match_lat and match_lon:
            latitud = float(match_lat.group(1))   # group(1) es lo que capturaron los paréntesis del patrón
            longitud = float(match_lon.group(1))
            coordenadas_por_bloque[numero_bloque] = {"latitud": latitud, "longitud": longitud}
        # Si falta latitude o longitude en este bloque, simplemente lo omitimos (sin error)

    return coordenadas_por_bloque


def buscar_coordenada(coordenadas_por_bloque: dict, numero_fotograma: int):
    """
    Dado el número de fotograma (empieza en 0 en nuestro sistema),
    devuelve su coordenada correspondiente del .SRT (que empieza en 1), o None si no existe.
    """
    numero_bloque = numero_fotograma + 1  # offset: nuestro fotograma 0 = bloque SRT 1
    return coordenadas_por_bloque.get(numero_bloque)