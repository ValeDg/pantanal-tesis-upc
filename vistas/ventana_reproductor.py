import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
from procesamiento.detector_color import detectar_zonas_color, dibujar_detecciones
from modelos.anomalia import guardar_anomalias
from modelos.monitoreo import marcar_como_procesado
from tkinter import messagebox


class VentanaReproductor(ctk.CTkToplevel):
    def __init__(self, padre, id_monitoreo: int, ruta_video: str, cada_n_fotogramas: int = 15):
        super().__init__(padre)
        self.title("Procesar y Visualizar - Análisis Térmico")
        self.geometry("900x600")

        self.id_monitoreo = id_monitoreo
        self.ruta_video = ruta_video
        self.cada_n_fotogramas = cada_n_fotogramas
        self.captura = cv2.VideoCapture(ruta_video)
        self.reproduciendo = False
        self.ya_guardado = False  

        self.contador_fotograma = 0
        self.anomalias_acumuladas = []  

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
# Para rebobinar al inicio para poder volver a reproducir (solo el visual)
            self.captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        self.after(33, self._loop_reproduccion)

    def _mostrar_siguiente_fotograma(self):
        exito, imagen = self.captura.read()

        if not exito:
            return False

        anomalias = detectar_zonas_color(imagen)
        imagen_dibujada = dibujar_detecciones(imagen, anomalias, self.colores_activos)

        self._actualizar_widget_imagen(imagen_dibujada)
        self.label_contador.configure(text=f"Zonas en pantalla: {len(anomalias)}")

# Solo ACUMULAMOS para guardar cada N fotogramas, aunque dibujamos en TODOS para que se vea mas fluido

        if self.contador_fotograma % self.cada_n_fotogramas == 0:
            for anomalia in anomalias:
                anomalia["fotograma_num"] = self.contador_fotograma
                self.anomalias_acumuladas.append(anomalia)

        self.contador_fotograma += 1
        return True

    def _actualizar_widget_imagen(self, imagen_bgr):
        imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen_rgb)
        imagen_pil.thumbnail((760, 560))

# CTkImage en vez de ImageTk.PhotoImage para que se ve bien en pantallas HighDPI
        imagen_ctk = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=imagen_pil.size)

        self.imagen_actual = imagen_ctk
        self.label_video.configure(image=imagen_ctk)

    def _finalizar_procesamiento(self):
        """Se llama cuando el video termina solo, o al cerrar la ventana."""
        if self.ya_guardado:
            return

        guardar_anomalias(self.id_monitoreo, self.anomalias_acumuladas)
        marcar_como_procesado(self.id_monitoreo)
        self.ya_guardado = True

        total = len(self.anomalias_acumuladas)
        self.label_resultado.configure(
            text=f"✓ Procesado.\n{total} anomalías guardadas.",
            text_color="green"
        )

# Popup para que el resultado sea imposible de pasar por alto, incluso si el usuario cierra la 
# ventana antes de que termine el video

        messagebox.showinfo("Procesamiento completado", f"Se detectaron {total} zonas anómalas en total.")

    def _al_cerrar(self):
        self.reproduciendo = False

# Si el usuario cierra a mitad de la reproducción, igual se guarda
# lo detectado hasta ese punto
        self._finalizar_procesamiento()
        self.captura.release()
        self.destroy()