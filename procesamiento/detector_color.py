import cv2
import numpy as np

RANGOS_COLOR = {
    "verde": [
        (np.array([35, 80, 80]), np.array([85, 255, 255]))
    ],
    "naranja": [
        (np.array([10, 100, 100]), np.array([25, 255, 255]))
    ],
    "rojo": [
        (np.array([0, 100, 100]), np.array([9, 255, 255])),
        (np.array([170, 100, 100]), np.array([179, 255, 255])),
    ],
}

# Colores BGR (formato OpenCV) para dibujar cada rectángulo en pantalla
COLOR_DIBUJO_BGR = {
    "rojo": (0, 0, 255),
    "naranja": (0, 165, 255),
    "verde": (0, 255, 0),
}

AREA_MINIMA_ANOMALIA = 150


def detectar_zonas_color(imagen):
    """
    Devuelve una lista de anomalías detectadas en el fotograma:
    [{"nivel": "rojo", "pos_x": 120, "pos_y": 340,
      "rect": (x, y, ancho, alto)}, ...]
    """
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    anomalias_encontradas = []

    for nivel, rangos in RANGOS_COLOR.items():
        mascara_total = None
        for rango_bajo, rango_alto in rangos:
            mascara = cv2.inRange(imagen_hsv, rango_bajo, rango_alto)
            mascara_total = mascara if mascara_total is None else cv2.bitwise_or(mascara_total, mascara)

        contornos, _ = cv2.findContours(mascara_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if area < AREA_MINIMA_ANOMALIA:
                continue

            momentos = cv2.moments(contorno)
            if momentos["m00"] == 0:
                continue
            centro_x = int(momentos["m10"] / momentos["m00"])
            centro_y = int(momentos["m01"] / momentos["m00"])

    # Rectangulo dibujado para mostrar los obejtos detectados
            x, y, ancho, alto = cv2.boundingRect(contorno)

            anomalias_encontradas.append({
                "nivel": nivel,
                "pos_x": centro_x,
                "pos_y": centro_y,
                "rect": (x, y, ancho, alto),
            })

    return anomalias_encontradas


def dibujar_detecciones(imagen, anomalias, colores_activos=None):
    """
    Dibuja un rectángulo sobre la imagen por cada anomalía detectada.
    colores_activos: set opcional, ej. {"rojo", "naranja"} — si se pasa,
    solo dibuja esos niveles (para los checkboxes de la interfaz).
    No modifica la imagen original: trabaja sobre una copia.
    """
    imagen_dibujada = imagen.copy()

    for anomalia in anomalias:
        nivel = anomalia["nivel"]
        if colores_activos is not None and nivel not in colores_activos:
            continue

        x, y, ancho, alto = anomalia["rect"]
        color_bgr = COLOR_DIBUJO_BGR[nivel]

        cv2.rectangle(imagen_dibujada, (x, y), (x + ancho, y + alto), color_bgr, 2)
        cv2.putText(imagen_dibujada, nivel, (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 1)

    return imagen_dibujada