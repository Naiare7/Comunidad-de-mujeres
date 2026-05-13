# Dependencias reutilizables para los endpoints.
# La más importante es get_current_user, que protege las rutas privadas.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User


# HTTPBearer extrae automáticamente el token del header "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependencia que verifica el token JWT y devuelve la usuaria autenticada.
    Se usa en cualquier endpoint que requiera estar logueada:
        @router.get("/ruta-privada")
        async def ruta(user: User = Depends(get_current_user)):
    """
    token = credentials.credentials  # El token en texto

    # Intentamos decodificar el token. Si está mal firmado o expirado, lanzamos error 401.
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")  # "sub" (subject) es el ID de la usuaria
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    # Buscamos la usuaria en la base de datos por su ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuaria no encontrada")

    return user
