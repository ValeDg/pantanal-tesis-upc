import json
from db.conexion import obtener_conexion


def crear_cultivo(nombre: str, area_ha: float, ubicacion: str, poligono: list = None) -> int:
    """
    poligono: lista de [lat, lon] o None si no se definió (compatibilidad con cultivos viejos)
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    poligono_json = json.dumps(poligono) if poligono else None

    cursor.execute(
        "INSERT INTO cultivos (nombre, area_ha, ubicacion, poligono) VALUES (?, ?, ?, ?)",
        (nombre, area_ha, ubicacion, poligono_json)
    )
    id_generado = cursor.lastrowid

    conexion.commit()
    conexion.close()
    return id_generado


def listar_cultivos() -> list:
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cultivo, nombre FROM cultivos ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return filas


def obtener_poligono_cultivo(id_cultivo: int):
    """
    Devuelve el polígono del cultivo como lista de [lat, lon], o None si no tiene.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT poligono FROM cultivos WHERE id_cultivo = ?", (id_cultivo,))
    fila = cursor.fetchone()
    conexion.close()

    if fila is None or fila["poligono"] is None:
        return None

    return json.loads(fila["poligono"])  # convierte el texto JSON de vuelta a lista de Python