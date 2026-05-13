# Rutas de autenticación: registro, login, etc.
# Cada función es un endpoint de la API.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_reset_token, verify_reset_token
from app.models.user import User
from app.schemas.auth import UserCreate, ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, UserResponse, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra una nueva usuaria.
    1. Comprueba que el email y el nombre de usuario no estén ya en uso.
    2. Guarda la usuaria con la contraseña cifrada.
    3. Devuelve un token JWT para que pueda autenticarse de inmediato.
    """
    # Normalizamos el email a minúsculas para evitar duplicados por mayúsculas
    email = payload.email.lower().strip()

    # Comprobamos si el email ya existe (búsqueda insensible a mayúsculas)
    existing_email = await db.execute(select(User).where(func.lower(User.email) == email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    # Comprobamos si el nombre de usuario ya existe
    existing_username = await db.execute(select(User).where(User.username == payload.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya está en uso",
        )

    # Creamos la usuaria con la contraseña cifrada
    new_user = User(
        username=payload.username,
        email=email,
        hashed_password=hash_password(payload.password),
    )

    db.add(new_user)
    await db.commit()           # Guarda los cambios en la base de datos
    await db.refresh(new_user)  # Recarga el objeto para obtener el ID generado

    # Creamos el token JWT con el ID de la usuaria como identificador
    token = create_access_token(data={"sub": new_user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Inicia sesión con email y contraseña.
    1. Busca la usuaria por email.
    2. Comprueba que la contraseña coincida.
    3. Devuelve un token JWT para autenticar las siguientes peticiones.
    """
    # Normalizamos el email a minúsculas (igual que en el registro)
    email = payload.email.lower().strip()

    # Buscamos la usuaria en la base de datos por email
    result = await db.execute(select(User).where(func.lower(User.email) == email))
    user = result.scalar_one_or_none()

    # Si no existe o la contraseña no coincide, devolvemos error 401
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # Creamos un token JWT nuevo para esta sesión
    token = create_access_token(data={"sub": user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Solicita un enlace de recuperación de contraseña.
    1. Busca la usuaria por email.
    2. Si existe, genera un token JWT que expira en 24 horas.
    3. En producción se enviaría por email; aquí solo lo imprimimos.
    Por seguridad, siempre devolvemos el mismo mensaje (no revelamos si el email existe).
    """
    email = payload.email.lower().strip()

    # Buscamos la usuaria en la base de datos
    result = await db.execute(select(User).where(func.lower(User.email) == email))
    user = result.scalar_one_or_none()

    # Solo generamos token si la usuaria existe (pero no lo revelamos en la respuesta)
    if user:
        reset_token = create_reset_token(data={"sub": user.email})
        # En producción aquí iría el envío de email real
        print(f"Token de recuperación para {user.email}: {reset_token}")

    # Siempre devolvemos el mismo mensaje por seguridad
    return {"message": "Si el email está registrado, recibirás un enlace de recuperación"}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Restablece la contraseña usando el token de recuperación.
    1. Valida el token JWT (expiración 24h) y extrae el email.
    2. Busca la usuaria por email.
    3. Actualiza la contraseña con la nueva (cifrada con bcrypt).
    """
    # Verificamos el token y obtenemos el email de la usuaria
    email = verify_reset_token(payload.token)

    # Buscamos la usuaria en la base de datos por email
    result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrada",
        )

    # Actualizamos la contraseña (ya viene validada por el schema Pydantic)
    user.hashed_password = hash_password(payload.password)
    await db.commit()

    return {"message": "Contraseña restablecida correctamente"}
