import customtkinter as ctk
from tkinter import messagebox   # los messagebox de tkinter normal siguen funcionando bien
from modelos.cultivo import crear_cultivo
from utils.validaciones import validar_cultivo


class FormularioCultivo(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Registrar Cultivo")
        self.geometry("380x280")
        self.resizable(False, False)

        self.var_nombre = ctk.StringVar()
        self.var_area = ctk.StringVar()
        self.var_ubicacion = ctk.StringVar()

        self._construir_formulario()

    def _construir_formulario(self):
        # padding (padx/pady) más generoso: se ve mejor con el estilo redondeado
        ctk.CTkLabel(self, text="Registrar Cultivo", font=ctk.CTkFont(size=18, weight="bold")) \
            .grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15))

        ctk.CTkLabel(self, text="Nombre del cultivo:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_nombre, width=180).grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Área (hectáreas):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_area, width=180).grid(row=2, column=1, padx=20, pady=10)

        ctk.CTkLabel(self, text="Ubicación:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.var_ubicacion, width=180).grid(row=3, column=1, padx=20, pady=10)

        ctk.CTkButton(self, text="Guardar", command=self._guardar) \
            .grid(row=4, column=0, columnspan=2, pady=25)

    def _guardar(self):
        nombre = self.var_nombre.get()
        area_texto = self.var_area.get()
        ubicacion = self.var_ubicacion.get()

        es_valido, mensaje_error, area_num = validar_cultivo(nombre, area_texto, ubicacion)

        if not es_valido:
            messagebox.showerror("Datos inválidos", mensaje_error)
            return

        id_cultivo = crear_cultivo(nombre, area_num, ubicacion)
        messagebox.showinfo("Éxito", f"Cultivo registrado con ID {id_cultivo}")
        self.destroy()