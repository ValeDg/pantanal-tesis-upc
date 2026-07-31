from db.conexion import obtener_conexion


def crear_monitoreo(id_cultivo: int, fecha: str, observaciones: str,
                     ruta_video: str, ruta_gps: str | None) -> int:
    """
    Inserta un nuevo monitoreo, ya con su video y GPS (o None si no hay GPS).
    Devuelve el id_monitoreo generado.
    """
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