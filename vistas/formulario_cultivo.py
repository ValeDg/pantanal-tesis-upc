import customtkinter as ctk
from tkinter import messagebox
from modelos.cultivo import crear_cultivo
from utils.validaciones import validar_cultivo


class FormularioCultivo(ctk.CTkToplevel):
    def __init__(self, padre, al_guardar_callback=None):
        super().__init__(padre)
        self.title("Registrar Cultivo")
        self.geometry("380x380")
        self.resizable(False, False)

        self.al_guardar_callback = al_guardar_callback
        self.poligono_definido = None  # se llena cuando el usuario dibuja el área en el mapa

        self.var_nombre = ctk.StringVar()
        self.var_area = ctk.StringVar()
        self.var_ubicacion = ctk.StringVar()

        self._construir_formulario()

    def _construir_formulario(self):
        ctk.CTkLabel(self, text="Registrar Cultivo", font=ctk.CTkFont(size=18, weight="bold")) \
            .grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15))

        ctk.CTkLabel(self, text="Nombre del cultivo:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_nombre, width=180).grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Área (hectáreas):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_area, width=180).grid(row=2, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Ubicación:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_ubicacion, width=180).grid(row=3, column=1, padx=20, pady=10)

        ctk.CTkButton(self, text="🗺️ Dibujar área en mapa", command=self._abrir_mapa) \
            .grid(row=4, column=0, columnspan=2, pady=(15, 5))
        self.label_poligono = ctk.CTkLabel(self, text="Área no definida", text_color="gray")
        self.label_poligono.grid(row=5, column=0, columnspan=2)

        ctk.CTkButton(self, text="Guardar", command=self._guardar) \
            .grid(row=6, column=0, columnspan=2, pady=25)

    def _abrir_mapa(self):
        from vistas.mapa_poligono import MapaPoligono
        MapaPoligono(self, al_confirmar_callback=self._al_confirmar_poligono)

    def _al_confirmar_poligono(self, poligono):
        self.poligono_definido = poligono
        self.label_poligono.configure(text=f"✓ Área definida ({len(poligono)} puntos)", text_color="green")

    def _guardar(self):
        nombre = self.var_nombre.get()
        area_texto = self.var_area.get()
        ubicacion = self.var_ubicacion.get()

        es_valido, mensaje_error, area_num = validar_cultivo(nombre, area_texto, ubicacion)

        if not es_valido:
            messagebox.showerror("Datos inválidos", mensaje_error)
            return

        if self.poligono_definido is None:
            respuesta = messagebox.askyesno(
                "Sin área definida",
                "No dibujaste el área del cultivo en el mapa.\n\n"
                "Sin esto, el sistema no podrá filtrar correctamente las detecciones "
                "durante el procesamiento (HU-007).\n\n¿Deseas guardar de todas formas?"
            )
            if not respuesta:
                return

        id_cultivo = crear_cultivo(nombre, area_num, ubicacion, self.poligono_definido)
        messagebox.showinfo("Éxito", f"Cultivo registrado con ID {id_cultivo}")

        if self.al_guardar_callback:
            self.al_guardar_callback()

        self.destroy()