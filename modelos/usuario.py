from db.conexion import obtener_conexion


def crear_usuario(nombre: str, correo: str, contrasena_hash: str, rol: str) -> int:
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO usuarios (nombre, correo, contrasena_hash, rol, activo)
           VALUES (?, ?, ?, ?, 1)""",
        (nombre, correo, contrasena_hash, rol)
    )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado


def obtener_usuario_por_correo(correo: str):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
    fila = cursor.fetchone()
    conexion.close()
    return fila  # None si no existe


def contar_usuarios() -> int:
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    total = cursor.fetchone()["total"]
    conexion.close()
    return total


def listar_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario, nombre, correo, rol, activo FROM usuarios ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return filas


def cambiar_estado_usuario(id_usuario: int, activo: bool):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET activo = ? WHERE id_usuario = ?", (1 if activo else 0, id_usuario))
    conexion.commit()
    conexion.close()