import sqlite3
import os

RUTA_DB = os.path.join(os.path.dirname(__file__), "pantanal.db")


def obtener_conexion():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

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

    # --- NUEVA: tabla de anomalías detectadas (SPRINT 2) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomalias (
            id_anomalia    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_monitoreo   INTEGER NOT NULL,
            nivel          TEXT NOT NULL,
            fotograma_num  INTEGER NOT NULL,
            pos_x          INTEGER,
            pos_y          INTEGER,
            latitud        REAL,
            longitud       REAL,
            FOREIGN KEY (id_monitoreo) REFERENCES monitoreos(id_monitoreo)
        )
    """)

    conexion.commit()
    conexion.close()