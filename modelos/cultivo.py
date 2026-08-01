from db.conexion import obtener_conexion


def crear_cultivo(nombre: str, area_ha: float, ubicacion: str) -> int:
    """
    Inserta un nuevo cultivo en la base de datos.
    Devuelve el id_cultivo generado automáticamente.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO cultivos (nombre, area_ha, ubicacion) VALUES (?, ?, ?)",
        (nombre, area_ha, ubicacion)
    )
# cursor.lastrowid da el id que SQLite acaba de asignar (AUTOINCREMENT)
    id_generado = cursor.lastrowid

    conexion.commit()
    conexion.close()
    return id_generado


def listar_cultivos() -> list:
    """
    Devuelve todos los cultivos registrados, útil para el formulario
    de monitoreo (HU-002) donde el usuario elige a qué cultivo pertenece.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cultivo, nombre FROM cultivos ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return filas