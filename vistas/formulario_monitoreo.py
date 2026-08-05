import customtkinter as ctk
from tkinter import messagebox, filedialog
from modelos.cultivo import listar_cultivos
from modelos.monitoreo import crear_monitoreo
from utils.validaciones import validar_monitoreo
from utils.archivos import copiar_archivo


class FormularioMonitoreo(ctk.CTkToplevel):
    def __init__(self, padre, al_guardar_callback=None):
        super().__init__(padre)
        self.title("Registrar Monitoreo")
        self.geometry("420x420")
        self.resizable(False, False)

        self.al_guardar_callback = al_guardar_callback

# Rutas seleccionadas por el usuario (empiezan vacías)
        self.ruta_video_seleccionada = None
        self.ruta_gps_seleccionada = None

# Mapeo nombre -> id_cultivo, para traducir lo que elige el ComboBox
        self.mapa_cultivos = {}

        self.var_cultivo = ctk.StringVar()
        self.var_fecha = ctk.StringVar()
        self.var_observaciones = ctk.StringVar()

        self._construir_formulario()

    def _construir_formulario(self):
        ctk.CTkLabel(self, text="Registrar Monitoreo", font=ctk.CTkFont(size=18, weight="bold")) \
            .grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15))

# --- Cultivo (ComboBox poblado dinámicamente) ---
        ctk.CTkLabel(self, text="Cultivo:").grid(row=1, column=0, padx=20, pady=8, sticky="w")
        cultivos = listar_cultivos()
        nombres_cultivos = []
        for fila in cultivos:
            texto_mostrado = f"#{fila['id_cultivo']} - {fila['nombre']}"  # único, sin ambigüedad
            nombres_cultivos.append(texto_mostrado)
            self.mapa_cultivos[texto_mostrado] = fila["id_cultivo"]

        self.combo_cultivo = ctk.CTkComboBox(self, values=nombres_cultivos, variable=self.var_cultivo, width=200)
        self.combo_cultivo.grid(row=1, column=1, padx=20, pady=8)

    # --- Fecha ---
        ctk.CTkLabel(self, text="Fecha (AAAA-MM-DD):").grid(row=2, column=0, padx=20, pady=8, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_fecha, width=200).grid(row=2, column=1, padx=20, pady=8)

    # --- Observaciones ---
        ctk.CTkLabel(self, text="Observaciones:").grid(row=3, column=0, padx=20, pady=8, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_observaciones, width=200).grid(row=3, column=1, padx=20, pady=8)

    # --- Carga de video ---
        ctk.CTkButton(self, text="Cargar video (.MP4)", command=self._seleccionar_video) \
            .grid(row=4, column=0, columnspan=2, pady=(20, 5))
        self.label_video = ctk.CTkLabel(self, text="Ningún video seleccionado", text_color="gray")
        self.label_video.grid(row=5, column=0, columnspan=2)

    # --- Carga de GPS (OPCIONAL POR) ---
        ctk.CTkButton(self, text="Cargar GPS (.SRT) - Opcional", command=self._seleccionar_gps) \
            .grid(row=6, column=0, columnspan=2, pady=(15, 5))
        self.label_gps = ctk.CTkLabel(self, text="Sin archivo GPS (opcional)", text_color="gray")
        self.label_gps.grid(row=7, column=0, columnspan=2)

    # --- Guardar ---
        ctk.CTkButton(self, text="Guardar Monitoreo", command=self._guardar) \
            .grid(row=8, column=0, columnspan=2, pady=25)

    def _seleccionar_video(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el video térmico",
            filetypes=[("Video MP4", "*.mp4")]
        )
        if ruta:
            self.ruta_video_seleccionada = ruta
            self.label_video.configure(text=f"✓ {ruta.split('/')[-1]}", text_color="green")

    def _seleccionar_gps(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo GPS",
            filetypes=[("Archivo SRT", "*.srt")]
        )
        if ruta:
            self.ruta_gps_seleccionada = ruta
            self.label_gps.configure(text=f"✓ {ruta.split('/')[-1]}", text_color="green")

    def _guardar(self):
        nombre_cultivo = self.var_cultivo.get()
        id_cultivo = self.mapa_cultivos.get(nombre_cultivo)
        fecha = self.var_fecha.get()
        observaciones = self.var_observaciones.get()

        es_valido, mensaje_error = validar_monitoreo(
            id_cultivo, fecha, self.ruta_video_seleccionada, self.ruta_gps_seleccionada
        )

        if not es_valido:
            messagebox.showerror("Datos inválidos", mensaje_error)
            return

        ruta_video_final = copiar_archivo(self.ruta_video_seleccionada)
        ruta_gps_final = copiar_archivo(self.ruta_gps_seleccionada) if self.ruta_gps_seleccionada else None

        id_monitoreo = crear_monitoreo(id_cultivo, fecha, observaciones, ruta_video_final, ruta_gps_final)

        if self.al_guardar_callback:
            self.al_guardar_callback()

        quiere_procesar = messagebox.askyesno(
            "Monitoreo guardado",
            f"Monitoreo #{id_monitoreo} registrado correctamente.\n\n¿Deseas procesarlo ahora?"
        )

        if quiere_procesar:
            from vistas.ventana_reproductor import VentanaReproductor
            from modelos.cultivo import obtener_poligono_cultivo

            poligono = obtener_poligono_cultivo(id_cultivo)
            VentanaReproductor(self.master, id_monitoreo, ruta_video_final, ruta_gps_final, poligono=poligono)