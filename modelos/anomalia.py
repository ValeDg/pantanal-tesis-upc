from db.conexion import obtener_conexion


def guardar_anomalias(id_monitoreo: int, lista_anomalias: list):
    """
    Guarda todas las anomalías detectadas de un monitoreo de una sola vez.
    lista_anomalias: [{"nivel": ..., "fotograma_num": ..., "pos_x": ..., "pos_y": ...}, ...]
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    for anomalia in lista_anomalias:
        cursor.execute(
            """INSERT INTO anomalias (id_monitoreo, nivel, fotograma_num, pos_x, pos_y)
               VALUES (?, ?, ?, ?, ?)""",
            (id_monitoreo, anomalia["nivel"], anomalia["fotograma_num"],
             anomalia["pos_x"], anomalia["pos_y"])
        )

    conexion.commit()
    conexion.close()