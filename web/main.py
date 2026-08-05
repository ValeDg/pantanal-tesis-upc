from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from db.conexion import inicializar_base_datos
from modelos.usuario import obtener_usuario_por_correo, crear_usuario, contar_usuarios
from web.auth import generar_hash, verificar_contrasena, obtener_usuario_actual, requerir_rol

app = FastAPI(title="PANTANAL Web")

# La clave secreta firma las cookies de sesión — en un proyecto real esto
# NO debería estar escrito directamente en el código, pero para tu tesis
# (proyecto académico, uso local) es aceptable dejarlo así por simplicidad.
app.add_middleware(SessionMiddleware, secret_key="pantanal-clave-secreta-cambiar-en-produccion")

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.on_event("startup")
def al_iniciar():
    inicializar_base_datos()

    # Si no hay NINGÚN usuario todavía, creamos un administrador por defecto —
    # si no, nadie podría entrar nunca a crear el primer usuario (problema del huevo y la gallina)
    if contar_usuarios() == 0:
        crear_usuario(
            nombre="Administrador",
            correo="admin@pantanal.com",
            contrasena_hash=generar_hash("admin123"),
            rol="administrador"
        )
        print("Usuario administrador por defecto creado: admin@pantanal.com / admin123")


@app.get("/", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def procesar_login(request: Request, correo: str = Form(...), contrasena: str = Form(...)):
    usuario = obtener_usuario_por_correo(correo)

    credenciales_invalidas = (
        usuario is None
        or usuario["activo"] == 0
        or not verificar_contrasena(contrasena, usuario["contrasena_hash"])
    )

    if credenciales_invalidas:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Correo o contraseña incorrectos."}
        )

    # Guardamos el correo en la sesión — es lo único que necesitamos para
    # identificar al usuario en peticiones futuras (obtener_usuario_actual lo busca por esto)
    request.session["correo_usuario"] = usuario["correo"]

    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/logout")
def cerrar_sesion(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, usuario=Depends(obtener_usuario_actual)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "usuario": usuario})