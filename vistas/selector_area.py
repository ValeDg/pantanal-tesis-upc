import cv2
import customtkinter as ctk
from tkinter import Canvas, messagebox
from PIL import Image, ImageTk

TAMANO_HANDLE = 8  # radio en píxeles para detectar clic cerca de una esquina


class SelectorArea(ctk.CTkToplevel):
    def __init__(self, padre, ruta_video: str, al_confirmar_callback):
        super().__init__(padre)
        self.title("Selecciona el área del cultivo")
        self.resizable(False, False)

        self.al_confirmar_callback = al_confirmar_callback

        captura = cv2.VideoCapture(ruta_video)
        exito, primer_fotograma = captura.read()
        captura.release()

        if not exito:
            messagebox.showerror("Error", "No se pudo leer el video para seleccionar el área.")
            self.destroy()
            return

        self.alto_original, self.ancho_original = primer_fotograma.shape[:2]

        imagen_rgb = cv2.cvtColor(primer_fotograma, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen_rgb)
        imagen_pil.thumbnail((860, 520))
        self.ancho_mostrado, self.alto_mostrado = imagen_pil.size

        self.escala_x = self.ancho_original / self.ancho_mostrado
        self.escala_y = self.alto_original / self.alto_mostrado

        self.imagen_fondo = ImageTk.PhotoImage(imagen_pil)

        # roi_canvas guarda (x0, y0, x1, y1) en coordenadas de PANTALLA
        self.roi_canvas = None
        self.rectangulo_id = None
        self.handle_ids = {}  # {"nw": id, "ne": id, "sw": id, "se": id}

        self.modo_actual = None      # None | "dibujar" | "mover" | "redimensionar"
        self.esquina_activa = None   # "nw" | "ne" | "sw" | "se" (solo si modo == "redimensionar")
        self.punto_referencia = None  # último punto del mouse, para calcular el delta al mover

        self.geometry(f"{self.ancho_mostrado + 40}x{self.alto_mostrado + 160}")
        self._construir_interfaz()

    def _construir_interfaz(self):
        ctk.CTkLabel(self, text="Dibuja el área del cultivo. Arrastra las esquinas para ajustar,"
                                 " o el centro para mover todo el rectángulo.",
                     font=ctk.CTkFont(size=13, weight="bold"), wraplength=self.ancho_mostrado).pack(pady=10)

        self.canvas = Canvas(self, width=self.ancho_mostrado, height=self.alto_mostrado,
                              highlightthickness=0, cursor="cross")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.imagen_fondo)

        self.canvas.bind("<ButtonPress-1>", self._al_presionar)
        self.canvas.bind("<B1-Motion>", self._al_arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self._al_soltar)

        self.boton_confirmar = ctk.CTkButton(self, text="Confirmar área", state="disabled",
                                              command=self._confirmar)
        self.boton_confirmar.pack(pady=(15, 5))

        ctk.CTkButton(self, text="Usar video completo (sin recortar)", fg_color="transparent",
                      border_width=1, command=self._usar_completo).pack(pady=(0, 10))

    # ---------- Detección de qué se está tocando ----------

    def _esquina_bajo_cursor(self, x, y):
        """Devuelve 'nw'/'ne'/'sw'/'se' si (x,y) está cerca de esa esquina, o None."""
        if not self.roi_canvas:
            return None

        x0, y0, x1, y1 = self.roi_canvas
        esquinas = {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}

        for nombre, (ex, ey) in esquinas.items():
            if abs(x - ex) <= TAMANO_HANDLE and abs(y - ey) <= TAMANO_HANDLE:
                return nombre
        return None

    def _punto_dentro_del_rectangulo(self, x, y):
        if not self.roi_canvas:
            return False
        x0, y0, x1, y1 = self.roi_canvas
        return x0 <= x <= x1 and y0 <= y <= y1

    # ---------- Eventos del mouse ----------

    def _al_presionar(self, evento):
        esquina = self._esquina_bajo_cursor(evento.x, evento.y)

        if esquina:
            self.modo_actual = "redimensionar"
            self.esquina_activa = esquina
        elif self._punto_dentro_del_rectangulo(evento.x, evento.y):
            self.modo_actual = "mover"
            self.punto_referencia = (evento.x, evento.y)
        else:
            self.modo_actual = "dibujar"
            self.punto_referencia = (evento.x, evento.y)
            self.roi_canvas = None  # empezamos un rectángulo nuevo desde cero

    def _al_arrastrar(self, evento):
        x = max(0, min(evento.x, self.ancho_mostrado))   # evita salirse del canvas
        y = max(0, min(evento.y, self.alto_mostrado))

        if self.modo_actual == "dibujar":
            x0, y0 = self.punto_referencia
            self.roi_canvas = (min(x0, x), min(y0, y), max(x0, x), max(y0, y))

        elif self.modo_actual == "redimensionar":
            x0, y0, x1, y1 = self.roi_canvas
            if self.esquina_activa == "nw":
                x0, y0 = x, y
            elif self.esquina_activa == "ne":
                x1, y0 = x, y
            elif self.esquina_activa == "sw":
                x0, y1 = x, y
            elif self.esquina_activa == "se":
                x1, y1 = x, y
            # Normalizamos por si el usuario arrastra una esquina "más allá" de la opuesta
            self.roi_canvas = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

        elif self.modo_actual == "mover":
            x_prev, y_prev = self.punto_referencia
            delta_x = x - x_prev
            delta_y = y - y_prev

            x0, y0, x1, y1 = self.roi_canvas
            ancho, alto = x1 - x0, y1 - y0

            # Movemos todo el rectángulo, pero sin dejar que se salga del canvas
            nuevo_x0 = max(0, min(x0 + delta_x, self.ancho_mostrado - ancho))
            nuevo_y0 = max(0, min(y0 + delta_y, self.alto_mostrado - alto))

            self.roi_canvas = (nuevo_x0, nuevo_y0, nuevo_x0 + ancho, nuevo_y0 + alto)
            self.punto_referencia = (x, y)

        self._redibujar()

    def _al_soltar(self, evento):
        self.modo_actual = None
        self.esquina_activa = None

        if self.roi_canvas:
            x0, y0, x1, y1 = self.roi_canvas
            if (x1 - x0) >= 10 and (y1 - y0) >= 10:
                self.boton_confirmar.configure(state="normal")
            else:
                self.roi_canvas = None
                self.boton_confirmar.configure(state="disabled")
                self._redibujar()

    # ---------- Dibujo en el canvas ----------

    def _redibujar(self):
        if self.rectangulo_id:
            self.canvas.delete(self.rectangulo_id)
        for handle_id in self.handle_ids.values():
            self.canvas.delete(handle_id)
        self.handle_ids = {}

        if not self.roi_canvas:
            return

        x0, y0, x1, y1 = self.roi_canvas
        self.rectangulo_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline="#00FF00", width=2)

        esquinas = {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}
        for nombre, (ex, ey) in esquinas.items():
            handle_id = self.canvas.create_rectangle(
                ex - TAMANO_HANDLE, ey - TAMANO_HANDLE, ex + TAMANO_HANDLE, ey + TAMANO_HANDLE,
                fill="#00FF00", outline="white"
            )
            self.handle_ids[nombre] = handle_id

    # ---------- Confirmación ----------

    def _confirmar(self):
        if not self.roi_canvas:
            return

        x0, y0, x1, y1 = self.roi_canvas
        x_real = int(x0 * self.escala_x)
        y_real = int(y0 * self.escala_y)
        ancho_real = int((x1 - x0) * self.escala_x)
        alto_real = int((y1 - y0) * self.escala_y)

        self.al_confirmar_callback((x_real, y_real, ancho_real, alto_real))
        self.destroy()

    def _usar_completo(self):
        self.al_confirmar_callback(None)
        self.destroy()