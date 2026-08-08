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

def listar_anomalias_de_monitoreo(id_monitoreo: int):
    """
    Agrupa las anomalías por combinación única de (nivel, coordenada),
    para no repetir cientos de filas casi idénticas cuando muchas detecciones
    caen en el mismo punto GPS (normal, ya que varias anomalías pueden
    compartir el mismo fotograma/coordenada).
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT nivel, latitud, longitud, COUNT(*) as cantidad
        FROM anomalias
        WHERE id_monitoreo = ?
        GROUP BY nivel, latitud, longitud
        ORDER BY nivel, cantidad DESC
    """, (id_monitoreo,))
    filas = cursor.fetchall()
    conexion.close()

    totales_por_nivel = {"rojo": 0, "naranja": 0, "verde": 0}
    for fila in filas:
        totales_por_nivel[fila["nivel"]] += fila["cantidad"]

    grupos_con_porcentaje = []
    for fila in filas:
        total_de_su_nivel = totales_por_nivel[fila["nivel"]]
        porcentaje = round(fila["cantidad"] / total_de_su_nivel * 100, 1) if total_de_su_nivel > 0 else 0

        grupos_con_porcentaje.append({
            "nivel": fila["nivel"],
            "latitud": fila["latitud"],
            "longitud": fila["longitud"],
            "cantidad": fila["cantidad"],
            "porcentaje_categoria": porcentaje,
        })

    return grupos_con_porcentaje

def obtener_estadisticas_globales():
    """Estadísticas agregadas de TODOS los monitoreos, para el dashboard."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT nivel, COUNT(*) as cantidad FROM anomalias GROUP BY nivel")
    conteos = {"rojo": 0, "naranja": 0, "verde": 0}
    for fila in cursor.fetchall():
        conteos[fila["nivel"]] = fila["cantidad"]

    conexion.close()
    return conteos