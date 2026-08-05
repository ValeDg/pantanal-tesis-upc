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