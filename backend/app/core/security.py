# Funciones de seguridad: contraseñas y tokens JWT.

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# CryptContext gestiona el hashing de contraseñas con bcrypt.
# Nunca guardamos la contraseña en texto plano, solo su "hash" (versión cifrada irreversible).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a su versión cifrada."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comprueba si una contraseña en texto plano coincide con su hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_reset_token(data: dict) -> str:
    """
    Crea un token JWT para recuperación de contraseña.
    Este token expira en 24 horas (mientras que el de acceso dura más tiempo).
    """
    payload = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    payload["exp"] = expiration
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_reset_token(token: str) -> str:
    """
    Decodifica un token de recuperación y devuelve el email si es válido.
    Si el token expiró o está mal formado, lanza una excepción HTTP 400.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido",
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace ha expirado o es inválido",
        )


def create_access_token(data: dict) -> str:
    """
    Crea un token JWT firmado con los datos proporcionados.
    El token incluye una fecha de expiración y se firma con la clave secreta.
    JWT (JSON Web Token) es un estándar para transmitir información de forma segura.
    """
    payload = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(days=settings.access_token_expire_days)
    payload["exp"] = expiration  # "exp" es el campo estándar de expiración en JWT
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
