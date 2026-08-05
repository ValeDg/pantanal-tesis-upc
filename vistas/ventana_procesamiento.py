import customtkinter as ctk
from tkinter import messagebox
from modelos.monitoreo import listar_monitoreos_pendientes


class VentanaProcesamiento(ctk.CTkToplevel):
    def __init__(self, padre):
        super().__init__(padre)
        self.title("Procesar Monitoreo")
        self.geometry("450x300")
        self.resizable(False, False)

        self.mapa_monitoreos = {}
        self.var_monitoreo = ctk.StringVar()

        self._construir_formulario()

    def _construir_formulario(self):
        ctk.CTkLabel(self, text="Procesar Monitoreo", font=ctk.CTkFont(size=18, weight="bold")) \
            .pack(padx=20, pady=(20, 15))

        pendientes = listar_monitoreos_pendientes()

        if not pendientes:
            ctk.CTkLabel(self, text="No hay monitoreos pendientes de procesar.") \
                .pack(padx=20, pady=20)
            return

        opciones = []
        for fila in pendientes:
            texto = f"#{fila['id_monitoreo']} - {fila['nombre_cultivo']} - {fila['fecha']}"
            opciones.append(texto)
            self.mapa_monitoreos[texto] = fila["id_monitoreo"]

        ctk.CTkLabel(self, text="Selecciona un monitoreo:").pack(padx=20, pady=(10, 5))
        ctk.CTkComboBox(self, values=opciones, variable=self.var_monitoreo, width=320) \
            .pack(padx=20, pady=5)

        ctk.CTkButton(self, text="Procesar", command=self._procesar) \
            .pack(padx=20, pady=25)

    def _procesar(self):
        from vistas.ventana_reproductor import VentanaReproductor
        from modelos.cultivo import obtener_poligono_cultivo

        texto_elegido = self.var_monitoreo.get()
        id_monitoreo = self.mapa_monitoreos.get(texto_elegido)

        if id_monitoreo is None:
            messagebox.showerror("Error", "Debes seleccionar un monitoreo.")
            return

        pendientes = listar_monitoreos_pendientes()
        fila_monitoreo = None
        for fila in pendientes:
            if fila["id_monitoreo"] == id_monitoreo:
                fila_monitoreo = fila
                break

        poligono = obtener_poligono_cultivo(fila_monitoreo["id_cultivo"])

        VentanaReproductor(
            self.master, id_monitoreo, fila_monitoreo["ruta_video"],
            fila_monitoreo["ruta_gps"], poligono=poligono
        )
        self.destroy()