import customtkinter as ctk
from db.conexion import inicializar_base_datos
from modelos.cultivo import listar_cultivos
from modelos.monitoreo import listar_monitoreos_pendientes
from vistas.formulario_cultivo import FormularioCultivo
from vistas.formulario_monitoreo import FormularioMonitoreo
from vistas.ventana_procesamiento import VentanaProcesamiento


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PANTANAL - Sistema de Monitoreo Térmico")
        self.geometry("420x560")

        self.tarjetas = {}  # guardadndo referencias para poder habilitar/deshabilitar después

        self._construir_interfaz()
        self.actualizar_estado()

    def _construir_interfaz(self):
        ctk.CTkLabel(self, text="🌾 PANTANAL", font=ctk.CTkFont(size=26, weight="bold")) \
            .pack(pady=(30, 0))
        ctk.CTkLabel(self, text="Sistema de Monitoreo Térmico", text_color="gray") \
            .pack(pady=(0, 10))

        self.label_resumen = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.label_resumen.pack(pady=(0, 25))

        self._crear_tarjeta(
            clave="cultivo", numero="①", icono="🌱", titulo="Registrar cultivo",
            descripcion="Da de alta un nuevo lote o cultivo",
            comando=lambda: FormularioCultivo(self, al_guardar_callback=self.actualizar_estado)
        )

        self._crear_tarjeta(
            clave="monitoreo", numero="②", icono="📡", titulo="Registrar monitoreo",
            descripcion="Carga un nuevo vuelo con video y GPS",
            comando=lambda: FormularioMonitoreo(self, al_guardar_callback=self.actualizar_estado)
        )

        self._crear_tarjeta(
            clave="procesar", numero="③", icono="⚙️", titulo="Procesar monitoreo",
            descripcion="Detecta anomalías térmicas en el video",
            comando=lambda: VentanaProcesamiento(self)
        )

    def _crear_tarjeta(self, clave, numero, icono, titulo, descripcion, comando):
        color_normal = ("gray90", "gray17")
        color_hover = ("gray80", "gray25")
        color_deshabilitado = ("gray95", "gray14")

        tarjeta = ctk.CTkFrame(self, corner_radius=12, fg_color=color_normal, cursor="hand2")
        tarjeta.pack(padx=30, pady=8, fill="x")

        contenido = ctk.CTkFrame(tarjeta, fg_color="transparent")
        contenido.pack(padx=15, pady=12, fill="x")

        label_titulo = ctk.CTkLabel(
            contenido, text=f"{numero}  {icono}  {titulo}",
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        label_titulo.pack(anchor="w")

        label_desc = ctk.CTkLabel(contenido, text=descripcion, text_color="gray", anchor="w")
        label_desc.pack(anchor="w")

# Guardando para poder habilitar - deshabilitar esta tarjeta después
        info_tarjeta = {
            "frame": tarjeta,
            "widgets": [tarjeta, contenido, label_titulo, label_desc],
            "comando": comando,
            "habilitada": True,
            "color_normal": color_normal,
            "color_hover": color_hover,
            "color_deshabilitado": color_deshabilitado,
        }
        self.tarjetas[clave] = info_tarjeta

# Se enlazó los mismos 3 eventos a cada widget de la tarjeta (el frame y los labels),
# reaccion cuando el mouse esté encima
        for widget in info_tarjeta["widgets"]:
            widget.bind("<Enter>", lambda event, c=clave: self._on_hover(c, True))
            widget.bind("<Leave>", lambda event, c=clave: self._on_hover(c, False))
            widget.bind("<Button-1>", lambda event, c=clave: self._on_click(c))

    def _on_hover(self, clave, esta_encima):
        info = self.tarjetas[clave]
        if not info["habilitada"]:
            return  # las tarjetas deshabilitadas no reaccionan al hover
        color = info["color_hover"] if esta_encima else info["color_normal"]
        info["frame"].configure(fg_color=color)

    def _on_click(self, clave):
        info = self.tarjetas[clave]
        if not info["habilitada"]:
            return  # clic ignorado si está deshabilitada
        info["comando"]()

    def actualizar_estado(self):
        cantidad_cultivos = len(listar_cultivos())
        cantidad_pendientes = len(listar_monitoreos_pendientes())

        self.label_resumen.configure(
            text=f"{cantidad_cultivos} cultivo(s) registrado(s)  ·  {cantidad_pendientes} por procesar"
        )

        info_monitoreo = self.tarjetas["monitoreo"]
        info_monitoreo["habilitada"] = cantidad_cultivos > 0

        color = info_monitoreo["color_normal"] if info_monitoreo["habilitada"] else info_monitoreo["color_deshabilitado"]
        info_monitoreo["frame"].configure(fg_color=color)
        cursor = "hand2" if info_monitoreo["habilitada"] else "arrow"
        info_monitoreo["frame"].configure(cursor=cursor)


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    inicializar_base_datos()

    app = VentanaPrincipal()
    app.mainloop()