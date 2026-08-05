import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkintermapview import TkinterMapView
from procesamiento.parser_gps import parsear_srt
from utils.geometria import envolvente_convexa


class MapaPoligono(ctk.CTkToplevel):
    def __init__(self, padre, al_confirmar_callback):
        super().__init__(padre)
        self.title("Define el área del cultivo")
        self.geometry("800x680")

        self.al_confirmar_callback = al_confirmar_callback
        self.puntos = []
        self.marcadores = []
        self.poligono_dibujado = None

        self._construir_interfaz()

    def _construir_interfaz(self):
        # --- Opción destacada: generar automáticamente ---
        panel_destacado = ctk.CTkFrame(self, corner_radius=12, fg_color=("gray85", "gray20"))
        panel_destacado.pack(padx=20, pady=(20, 10), fill="x")

        ctk.CTkLabel(
            panel_destacado, text="📡 Generar área automáticamente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 3))

        ctk.CTkLabel(
            panel_destacado,
            text="Recomendado: sube el archivo .SRT de un vuelo que haya\n"
                 "recorrido todo el cultivo. El área se dibuja sola.",
            text_color="gray", justify="center"
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            panel_destacado, text="Seleccionar archivo .SRT", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._generar_desde_srt
        ).pack(pady=(0, 18))

        # --- Separador ---
        panel_separador = ctk.CTkFrame(self, fg_color="transparent")
        panel_separador.pack(fill="x", padx=20, pady=(0, 5))
        ctk.CTkLabel(panel_separador, text="— o ajusta el área manualmente en el mapa —",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack()

        # --- Mapa (opción secundaria / de ajuste) ---
        self.mapa = TkinterMapView(self, width=760, height=380, corner_radius=8)
        self.mapa.pack(padx=20, pady=10)

        self.mapa.set_position(-8.3791, -74.5539)
        self.mapa.set_zoom(15)
        self.mapa.add_left_click_map_command(self._al_hacer_clic)

        panel_botones = ctk.CTkFrame(self, fg_color="transparent")
        panel_botones.pack(pady=5)

        ctk.CTkButton(panel_botones, text="Deshacer último punto", fg_color="transparent",
                      border_width=1, command=self._deshacer_ultimo).pack(side="left", padx=5)
        ctk.CTkButton(panel_botones, text="Reiniciar", fg_color="transparent",
                      border_width=1, command=self._reiniciar).pack(side="left", padx=5)
        self.boton_confirmar = ctk.CTkButton(panel_botones, text="Confirmar área",
                                              state="disabled", command=self._confirmar)
        self.boton_confirmar.pack(side="left", padx=5)

        self.label_estado = ctk.CTkLabel(self, text="0 puntos marcados", text_color="gray")
        self.label_estado.pack(pady=(5, 15))

    # ---------- Generación automática desde SRT ----------

    def _generar_desde_srt(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un archivo SRT de referencia (un vuelo que cubra el cultivo)",
            filetypes=[("Archivo SRT", "*.srt")]
        )
        if not ruta:
            return

        try:
            coordenadas_dict = parsear_srt(ruta)
        except (OSError, ValueError) as error:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {error}")
            return

        if len(coordenadas_dict) < 3:
            messagebox.showerror("Error", "El archivo no tiene suficientes puntos GPS válidos.")
            return

        puntos = [[v["latitud"], v["longitud"]] for v in coordenadas_dict.values()]
        poligono_generado = envolvente_convexa(puntos)

        self._reiniciar()
        self.puntos = [tuple(p) for p in poligono_generado]

        for lat, lon in self.puntos:
            marcador = self.mapa.set_marker(lat, lon)
            self.marcadores.append(marcador)

        self._redibujar_poligono()
        self._actualizar_estado()

        lat_promedio = sum(p[0] for p in self.puntos) / len(self.puntos)
        lon_promedio = sum(p[1] for p in self.puntos) / len(self.puntos)
        self.mapa.set_position(lat_promedio, lon_promedio)
        self.mapa.set_zoom(17)

        messagebox.showinfo(
            "Área generada",
            f"Se generó el área a partir de {len(coordenadas_dict)} puntos GPS del vuelo.\n\n"
            "Puedes ajustarla arrastrando los puntos en el mapa, o confirmarla tal cual."
        )

    # ---------- Interacción manual con el mapa ----------

    def _al_hacer_clic(self, coordenadas):
        lat, lon = coordenadas
        self.puntos.append((lat, lon))

        marcador = self.mapa.set_marker(lat, lon, text=str(len(self.puntos)))
        self.marcadores.append(marcador)

        self._redibujar_poligono()
        self._actualizar_estado()

    def _redibujar_poligono(self):
        if self.poligono_dibujado:
            self.poligono_dibujado.delete()
            self.poligono_dibujado = None

        if len(self.puntos) >= 3:
            self.poligono_dibujado = self.mapa.set_polygon(
                self.puntos, fill_color=None, outline_color="#00AA00", border_width=3
            )

    def _deshacer_ultimo(self):
        if not self.puntos:
            return
        self.puntos.pop()

        ultimo_marcador = self.marcadores.pop()
        ultimo_marcador.delete()

        self._redibujar_poligono()
        self._actualizar_estado()

    def _reiniciar(self):
        for marcador in self.marcadores:
            marcador.delete()
        self.marcadores = []
        self.puntos = []

        if self.poligono_dibujado:
            self.poligono_dibujado.delete()
            self.poligono_dibujado = None

        self._actualizar_estado()

    def _actualizar_estado(self):
        cantidad = len(self.puntos)
        self.label_estado.configure(text=f"{cantidad} punto(s) marcado(s)")
        self.boton_confirmar.configure(state="normal" if cantidad >= 3 else "disabled")

    def _confirmar(self):
        poligono_como_listas = [[lat, lon] for lat, lon in self.puntos]
        self.al_confirmar_callback(poligono_como_listas)
        self.destroy()