from db.conexion import obtener_conexion


def guardar_anomalias(id_monitoreo: int, lista_anomalias: list):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    for anomalia in lista_anomalias:
        cursor.execute(
            """INSERT INTO anomalias (id_monitoreo, nivel, fotograma_num, pos_x, pos_y, latitud, longitud)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (id_monitoreo, anomalia["nivel"], anomalia["fotograma_num"],
             anomalia["pos_x"], anomalia["pos_y"],
             anomalia.get("latitud"), anomalia.get("longitud"))
        )

    conexion.commit()
    conexion.close()

def obtener_resumen_monitoreo(id_monitoreo: int) -> dict:
    """
    Calcula el resumen del procesamiento de un monitoreo:
    porcentaje de área afectada, nivel predominante, y estado general.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT nivel, COUNT(*) as cantidad
        FROM anomalias
        WHERE id_monitoreo = ?
        GROUP BY nivel
    """, (id_monitoreo,))

    conteos = {"rojo": 0, "naranja": 0, "verde": 0}
    for fila in cursor.fetchall():
        conteos[fila["nivel"]] = fila["cantidad"]

    conexion.close()

    total = conteos["rojo"] + conteos["naranja"] + conteos["verde"]

    if total == 0:
        return {
            "total_zonas": 0, "conteos": conteos,
            "porcentaje_afectado": 0.0, "nivel_predominante": "sin datos",
            "estado_general": "Sin datos",
        }

    porcentaje_afectado = (conteos["rojo"] + conteos["naranja"]) / total * 100

    # max(conteos, key=conteos.get) devuelve la CLAVE cuyo valor es el más alto del diccionario
    nivel_predominante = max(conteos, key=conteos.get)

    mapa_estados = {"rojo": "Crítico", "naranja": "Moderado", "verde": "Normal"}
    estado_general = mapa_estados[nivel_predominante]

    return {
        "total_zonas": total,
        "conteos": conteos,
        "porcentaje_afectado": round(porcentaje_afectado, 1),
        "nivel_predominante": nivel_predominante,
        "estado_general": estado_general,
    }