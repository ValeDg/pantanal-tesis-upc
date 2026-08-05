from passlib.context import CryptContext
from fastapi import Request, HTTPException
from modelos.usuario import obtener_usuario_por_correo

# CryptContext es el "administrador" de algoritmos de hash de passlib.
# Le decimos que use bcrypt, el estándar recomendado actualmente.
contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generar_hash(contrasena: str) -> str:
    """Convierte una contraseña en texto plano a su hash seguro."""
    return contexto_hash.hash(contrasena)


def verificar_contrasena(contrasena_ingresada: str, hash_guardado: str) -> bool:
    """Compara una contraseña ingresada contra el hash guardado, sin revertir el hash."""
    return contexto_hash.verify(contrasena_ingresada, hash_guardado)


def obtener_usuario_actual(request: Request):
    """
    Revisa la sesión del navegador (la cookie) y devuelve el usuario logueado.
    Lanza un error 401 si no hay sesión válida — FastAPI lo convierte
    automáticamente en una respuesta HTTP de "no autorizado".
    """
    correo = request.session.get("correo_usuario")

    if not correo:
        raise HTTPException(status_code=401, detail="No has iniciado sesión")

    usuario = obtener_usuario_por_correo(correo)

    if usuario is None or usuario["activo"] == 0:
        raise HTTPException(status_code=401, detail="Sesión inválida")

    return usuario


def requerir_rol(*roles_permitidos):
    """
    Fábrica de dependencias: devuelve una función que verifica que el usuario
    actual tenga uno de los roles permitidos. Se usa así en las rutas:
    Depends(requerir_rol("administrador"))
    """
    def verificador(request: Request):
        usuario = obtener_usuario_actual(request)
        if usuario["rol"] not in roles_permitidos:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta sección")
        return usuario
    return verificador