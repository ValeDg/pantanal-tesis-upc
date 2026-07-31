import customtkinter as ctk
from db.conexion import inicializar_base_datos
from vistas.formulario_cultivo import FormularioCultivo
from vistas.formulario_monitoreo import FormularioMonitoreo

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    inicializar_base_datos()

    raiz = ctk.CTk()
    raiz.title("PANTANAL - Sistema de Monitoreo Térmico")
    raiz.geometry("350x220")

    ctk.CTkLabel(raiz, text="PANTANAL", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 10))

    ctk.CTkButton(raiz, text="Registrar nuevo cultivo",
                  command=lambda: FormularioCultivo(raiz)).pack(pady=8)

    ctk.CTkButton(raiz, text="Registrar nuevo monitoreo",
                  command=lambda: FormularioMonitoreo(raiz)).pack(pady=8)

    raiz.mainloop()