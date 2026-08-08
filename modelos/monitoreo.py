from db.conexion import obtener_conexion


def crear_monitoreo(id_cultivo: int, fecha: str, observaciones: str,
                     ruta_video: str, ruta_gps: str | None) -> int:
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO monitoreos
           (id_cultivo, fecha, observaciones, ruta_video, ruta_gps, estado)
           VALUES (?, ?, ?, ?, ?, 'registrado')""",
        (id_cultivo, fecha, observaciones, ruta_video, ruta_gps)
    )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado


def listar_monitoreos_pendientes():
    """Monitoreos que aún no han sido procesados (Sprint 2)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.id_monitoreo, m.id_cultivo, m.fecha, c.nombre AS nombre_cultivo, m.ruta_video, m.ruta_gps
        FROM monitoreos m
        JOIN cultivos c ON m.id_cultivo = c.id_cultivo
        WHERE m.estado = 'registrado'
        ORDER BY m.fecha DESC
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas

def marcar_como_procesado(id_monitoreo: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE monitoreos SET estado = 'procesado' WHERE id_monitoreo = ?",
        (id_monitoreo,)
    )
    conexion.commit()
    conexion.close()

def guardar_imagen_resultado(id_monitoreo: int, ruta_imagen: str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE monitoreos SET ruta_imagen_resultado = ? WHERE id_monitoreo = ?",
        (ruta_imagen, id_monitoreo)
    )
    conexion.commit()
    conexion.close()


def listar_monitoreos_procesados():
    """Monitoreos ya procesados, para la web (Encargado de Campo)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.id_monitoreo, m.fecha, c.nombre AS nombre_cultivo, m.ruta_imagen_resultado
        FROM monitoreos m
        JOIN cultivos c ON m.id_cultivo = c.id_cultivo
        WHERE m.estado = 'procesado'
        ORDER BY m.fecha DESC
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas


def obtener_monitoreo_por_id(id_monitoreo: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.*, c.nombre AS nombre_cultivo
        FROM monitoreos m
        JOIN cultivos c ON m.id_cultivo = c.id_cultivo
        WHERE m.id_monitoreo = ?
    """, (id_monitoreo,))
    fila = cursor.fetchone()
    conexion.close()
    return fila

def listar_monitoreos_procesados_filtrado(id_cultivo: int = None, fecha_desde: str = None, fecha_hasta: str = None):
    """
    Igual que listar_monitoreos_procesados, pero permite filtrar opcionalmente
    por cultivo y/o rango de fechas. Cualquier parámetro en None se ignora.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
        SELECT m.id_monitoreo, m.fecha, c.nombre AS nombre_cultivo, m.ruta_imagen_resultado
        FROM monitoreos m
        JOIN cultivos c ON m.id_cultivo = c.id_cultivo
        WHERE m.estado = 'procesado'
    """
    parametros = []

    if id_cultivo:
        consulta += " AND m.id_cultivo = ?"
        parametros.append(id_cultivo)

    if fecha_desde:
        consulta += " AND m.fecha >= ?"
        parametros.append(fecha_desde)

    if fecha_hasta:
        consulta += " AND m.fecha <= ?"
        parametros.append(fecha_hasta)

    consulta += " ORDER BY m.fecha DESC"

    cursor.execute(consulta, parametros)
    filas = cursor.fetchall()
    conexion.close()
    return filas

def listar_ultimos_monitoreos_con_ubicacion(cantidad: int = 5):
    """
    Últimos monitoreos procesados, con una coordenada aproximada
    (la primera anomalía con GPS que se encuentre), para mostrarlos en el mapa.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.id_monitoreo, m.fecha, c.nombre AS nombre_cultivo,
               (SELECT latitud FROM anomalias WHERE id_monitoreo = m.id_monitoreo AND latitud IS NOT NULL LIMIT 1) as latitud,
               (SELECT longitud FROM anomalias WHERE id_monitoreo = m.id_monitoreo AND longitud IS NOT NULL LIMIT 1) as longitud
        FROM monitoreos m
        JOIN cultivos c ON m.id_cultivo = c.id_cultivo
        WHERE m.estado = 'procesado'
        ORDER BY m.fecha DESC
        LIMIT ?
    """, (cantidad,))
    filas = cursor.fetchall()
    conexion.close()
    return filas