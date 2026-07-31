import customtkinter as ctk
from db.conexion import inicializar_base_datos
from vistas.formulario_cultivo import FormularioCultivo

if __name__ == "__main__":
    # Configuración global de tema — se hace UNA sola vez, antes de crear la ventana
    ctk.set_appearance_mode("system")      # "light", "dark" o "system" (sigue el tema de Windows)
    ctk.set_default_color_theme("blue")    # paleta de colores: "blue", "green", "dark-blue"

    inicializar_base_datos()

    raiz = ctk.CTk()
    raiz.title("PANTANAL - Sistema de Monitoreo Térmico")
    raiz.geometry("350x180")

    ctk.CTkLabel(raiz, text="PANTANAL", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 10))

    ctk.CTkButton(
        raiz,
        text="Registrar nuevo cultivo",
        command=lambda: FormularioCultivo(raiz)
    ).pack(pady=10)

    raiz.mainloop()