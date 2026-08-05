def punto_dentro_del_poligono(lat: float, lon: float, poligono: list) -> bool:
    """
    Algoritmo de "ray casting": determina si el punto (lat, lon) está
    dentro del polígono definido por una lista de puntos [[lat, lon], ...].

    Idea: trazamos una línea horizontal imaginaria hacia la derecha desde
    el punto, y contamos cuántas veces cruza los bordes del polígono.
    Impar = adentro, par = afuera.
    """
    if not poligono or len(poligono) < 3:
        return False  # un polígono necesita al menos 3 puntos para tener área

    dentro = False
    cantidad_puntos = len(poligono)

    # j empieza en el ÚLTIMO punto, para comparar cada lado con el anterior
    # (el polígono se "cierra" solo: el último punto conecta con el primero)
    j = cantidad_puntos - 1

    for i in range(cantidad_puntos):
        lat_i, lon_i = poligono[i]
        lat_j, lon_j = poligono[j]

        # Revisa si el borde entre el punto i y el punto j cruza
        # la línea horizontal a la altura de 'lat'
        cruza = ((lon_i > lon) != (lon_j > lon)) and \
                (lat < (lat_j - lat_i) * (lon - lon_i) / (lon_j - lon_i) + lat_i)

        if cruza:
            dentro = not dentro  # cada cruce "invierte" si estamos adentro o afuera

        j = i

    return dentro

def envolvente_convexa(puntos: list) -> list:
    """
    Calcula el envolvente convexo (convex hull) de una lista de puntos [lat, lon],
    usando el algoritmo de "monotone chain". Devuelve solo los puntos que forman
    el borde exterior, en orden, listos para usarse como polígono.
    """
    puntos_unicos = sorted(set(map(tuple, puntos)))  # quita duplicados y ordena por lat, luego lon

    if len(puntos_unicos) < 3:
        return [list(p) for p in puntos_unicos]  # no hay suficientes puntos para formar un área

    def producto_cruz(o, a, b):
        # Determina si al ir de o->a->b giramos a la izquierda (+) o derecha (-)
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Construimos la mitad inferior del envolvente
    inferior = []
    for punto in puntos_unicos:
        while len(inferior) >= 2 and producto_cruz(inferior[-2], inferior[-1], punto) <= 0:
            inferior.pop()
        inferior.append(punto)

    # Construimos la mitad superior (recorriendo los puntos al revés)
    superior = []
    for punto in reversed(puntos_unicos):
        while len(superior) >= 2 and producto_cruz(superior[-2], superior[-1], punto) <= 0:
            superior.pop()
        superior.append(punto)

    # Unimos ambas mitades (sin repetir los puntos de unión en los extremos)
    envolvente = inferior[:-1] + superior[:-1]

    return [list(p) for p in envolvente]