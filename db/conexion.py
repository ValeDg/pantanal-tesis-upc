import sqlite3
import os

# Ruta donde vivirá el archivo de base de datos.
# os.path.dirname(__file__) obtiene la carpeta donde está ESTE archivo (db/),
# así la ruta funciona sin importar desde dónde ejecutes main.py
RUTA_DB = os.path.join(os.path.dirname(__file__), "pantanal.db")


def obtener_conexion():
    """
    Abre y devuelve una conexión a la base de datos SQLite.
    Cada vez que necesitemos hablar con la BD, llamamos a esta función.
    """
    conexion = sqlite3.connect(RUTA_DB)
    # Esto permite acceder a las columnas por nombre (fila["nombre"])
    # en vez de solo por posición (fila[0]) — más legible y menos propenso a errores.
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_base_datos():
    """
    Crea las tablas si todavía no existen. Se llama una sola vez,
    al arrancar la aplicación (desde main.py).
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # IF NOT EXISTS evita error si ya corriste esto antes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cultivos (
            id_cultivo   INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL,
            area_ha      REAL NOT NULL,
            ubicacion    TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoreos (
            id_monitoreo   INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cultivo     INTEGER NOT NULL,
            fecha          TEXT NOT NULL,
            observaciones  TEXT,
            ruta_video     TEXT NOT NULL,
            ruta_gps       TEXT,
            estado         TEXT DEFAULT 'registrado',
            FOREIGN KEY (id_cultivo) REFERENCES cultivos(id_cultivo)
        )
    """)

    # Guarda los cambios en el archivo .db de forma permanente
    conexion.commit()
    # Siempre cerramos la conexión cuando terminamos de usarla
    conexion.close()