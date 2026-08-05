import cv2
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from procesamiento.detector_color import detectar_zonas_color, dibujar_detecciones
from procesamiento.parser_gps import parsear_srt, buscar_coordenada
from modelos.anomalia import guardar_anomalias, obtener_resumen_monitoreo
from utils.geometria import punto_dentro_del_poligono
import os
from modelos.monitoreo import marcar_como_procesado, guardar_imagen_resultado


class VentanaReproductor(ctk.CTkToplevel):
    def __init__(self, padre, id_monitoreo: int, ruta_video: str, ruta_gps: str = None,
                 poligono: list = None, cada_n_fotogramas: int = 15):
        super().__init__(padre)
        self.title("Procesar y Visualizar - Análisis Térmico")
        self.geometry("900x600")

        self.id_monitoreo = id_monitoreo
        self.ruta_video = ruta_video
        self.cada_n_fotogramas = cada_n_fotogramas
        self.poligono = poligono  # lista de [lat, lon] o None si el cultivo no lo tiene definido
        self.captura = cv2.VideoCapture(ruta_video)
        self.reproduciendo = False
        self.ya_guardado = False

        self.contador_fotograma = 0
        self.anomalias_acumuladas = []
        self.anomalias_descartadas_fuera_area = 0  # solo para mostrar en el resumen
    # ------------NUEVO-------------- SPRINT 3
        self.mejor_fotograma_imagen = None   # guarda la imagen (matriz) con más anomalías vistas
        self.mejor_fotograma_cantidad = -1    # cuántas anomalías tenía ese fotograma

        self.coordenadas_gps = {}
        if ruta_gps:
            try:
                self.coordenadas_gps = parsear_srt(ruta_gps)
            except (OSError, ValueError) as error:
                print(f"No se pudo leer el archivo GPS: {error}")

        self.colores_activos = {"rojo", "naranja", "verde"}
        self.var_rojo = ctk.BooleanVar(value=True)
        self.var_naranja = ctk.BooleanVar(value=True)
        self.var_verde = ctk.BooleanVar(value=True)

        self._construir_interfaz()
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _construir_interfaz(self):
        panel_controles = ctk.CTkFrame(self, width=200)
        panel_controles.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(panel_controles, text="Colores a detectar", font=ctk.CTkFont(weight="bold")) \
            .pack(pady=(10, 5))

        ctk.CTkCheckBox(panel_controles, text="Rojo", variable=self.var_rojo,
                         command=self._actualizar_colores_activos).pack(pady=5, anchor="w", padx=10)
        ctk.CTkCheckBox(panel_controles, text="Naranja", variable=self.var_naranja,
                         command=self._actualizar_colores_activos).pack(pady=5, anchor="w", padx=10)
        ctk.CTkCheckBox(panel_controles, text="Verde", variable=self.var_verde,
                         command=self._actualizar_colores_activos).pack(pady=5, anchor="w", padx=10)

        self.boton_reproducir = ctk.CTkButton(panel_controles, text="▶ Reproducir",
                                               command=self._alternar_reproduccion)
        self.boton_reproducir.pack(pady=20)

        self.label_contador = ctk.CTkLabel(panel_controles, text="Zonas en pantalla: 0")
        self.label_contador.pack(pady=5)

        texto_gps = f"📍 GPS: {len(self.coordenadas_gps)} puntos" if self.coordenadas_gps else "📍 Sin GPS"
        ctk.CTkLabel(panel_controles, text=texto_gps, text_color="gray").pack(pady=5)

        texto_poligono = "🗺️ Filtro: área del cultivo" if self.poligono else "🗺️ Filtro: ninguno (sin polígono)"
        ctk.CTkLabel(panel_controles, text=texto_poligono, text_color="gray", wraplength=170).pack(pady=5)

        self.label_resultado = ctk.CTkLabel(panel_controles, text="", text_color="gray", wraplength=170)
        self.label_resultado.pack(pady=15)

        self.label_video = ctk.CTkLabel(self, text="")
        self.label_video.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._mostrar_siguiente_fotograma()

    def _actualizar_colores_activos(self):
        self.colores_activos = set()
        if self.var_rojo.get():
            self.colores_activos.add("rojo")
        if self.var_naranja.get():
            self.colores_activos.add("naranja")
        if self.var_verde.get():
            self.colores_activos.add("verde")

    def _alternar_reproduccion(self):
        self.reproduciendo = not self.reproduciendo
        self.boton_reproducir.configure(text="⏸ Pausar" if self.reproduciendo else "▶ Reproducir")

        if self.reproduciendo:
            self._loop_reproduccion()

    def _loop_reproduccion(self):
        if not self.reproduciendo:
            return

        continuar = self._mostrar_siguiente_fotograma()

        if not continuar:
            self.reproduciendo = False
            self.boton_reproducir.configure(text="▶ Reproducir")
            self._finalizar_procesamiento()
            self.captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        self.after(33, self._loop_reproduccion)

    def _mostrar_siguiente_fotograma(self):
        exito, imagen = self.captura.read()

        if not exito:
            return False

        # Ya NO se pasa roi — analizamos el fotograma completo siempre
        anomalias = detectar_zonas_color(imagen)
        imagen_dibujada = dibujar_detecciones(imagen, anomalias, self.colores_activos)

        # Guardamos este fotograma como "el mejor" si tiene más anomalías que el candidato actual
        if len(anomalias) > self.mejor_fotograma_cantidad:
            self.mejor_fotograma_cantidad = len(anomalias)
            self.mejor_fotograma_imagen = imagen_dibujada.copy()

        self._actualizar_widget_imagen(imagen_dibujada)
        self.label_contador.configure(text=f"Zonas en pantalla: {len(anomalias)}")

        if self.contador_fotograma % self.cada_n_fotogramas == 0:
            coordenada = buscar_coordenada(self.coordenadas_gps, self.contador_fotograma)

            for anomalia in anomalias:
                anomalia["fotograma_num"] = self.contador_fotograma

                if coordenada:
                    anomalia["latitud"] = coordenada["latitud"]
                    anomalia["longitud"] = coordenada["longitud"]
                else:
                    anomalia["latitud"] = None
                    anomalia["longitud"] = None

                self._evaluar_y_acumular(anomalia)

        self.contador_fotograma += 1
        return True

    def _evaluar_y_acumular(self, anomalia):
        """
        Decide si esta anomalía se guarda o se descarta, según el filtro de polígono.
        """
        if self.poligono is None:
            # Sin polígono definido para el cultivo: no filtramos nada (comportamiento original)
            self.anomalias_acumuladas.append(anomalia)
            return

        if anomalia["latitud"] is None:
            # Hay polígono, pero esta anomalía no tiene coordenada GPS verificable → se descarta
            self.anomalias_descartadas_fuera_area += 1
            return

        esta_dentro = punto_dentro_del_poligono(anomalia["latitud"], anomalia["longitud"], self.poligono)

        if esta_dentro:
            self.anomalias_acumuladas.append(anomalia)
        else:
            self.anomalias_descartadas_fuera_area += 1

    def _actualizar_widget_imagen(self, imagen_bgr):
        imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen_rgb)
        imagen_pil.thumbnail((760, 560))

        imagen_ctk = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=imagen_pil.size)
        self.imagen_actual = imagen_ctk
        self.label_video.configure(image=imagen_ctk)

    def _finalizar_procesamiento(self):
        if self.ya_guardado:
            return

        guardar_anomalias(self.id_monitoreo, self.anomalias_acumuladas)
        marcar_como_procesado(self.id_monitoreo)
        self.ya_guardado = True

        if self.mejor_fotograma_imagen is not None:
            carpeta_resultados = "resultados_imagenes"
            os.makedirs(carpeta_resultados, exist_ok=True)
            ruta_imagen = os.path.join(carpeta_resultados, f"monitoreo_{self.id_monitoreo}.jpg")
            cv2.imwrite(ruta_imagen, self.mejor_fotograma_imagen)
            guardar_imagen_resultado(self.id_monitoreo, ruta_imagen)

        resumen = obtener_resumen_monitoreo(self.id_monitoreo)

        texto_descartadas = f"\n({self.anomalias_descartadas_fuera_area} descartadas, fuera del área)" \
            if self.poligono else ""

        self.label_resultado.configure(
            text=(
                f"✓ Procesado.\n"
                f"{resumen['total_zonas']} zonas detectadas.\n"
                f"Área afectada: {resumen['porcentaje_afectado']}%\n"
                f"Estado: {resumen['estado_general']}"
                f"{texto_descartadas}"
            ),
            text_color="green"
        )

        messagebox.showinfo(
            "Resumen del procesamiento",
            f"Estado general del cultivo: {resumen['estado_general']}\n\n"
            f"Zonas detectadas (dentro del cultivo): {resumen['total_zonas']}\n"
            f"  🔴 Rojo: {resumen['conteos']['rojo']}\n"
            f"  🟠 Naranja: {resumen['conteos']['naranja']}\n"
            f"  🟢 Verde: {resumen['conteos']['verde']}\n\n"
            f"Área afectada: {resumen['porcentaje_afectado']}%\n"
            f"Nivel predominante: {resumen['nivel_predominante']}"
            f"{texto_descartadas}"
        )

    def _al_cerrar(self):
        self.reproduciendo = False
        self._finalizar_procesamiento()
        self.captura.release()
        self.destroy()