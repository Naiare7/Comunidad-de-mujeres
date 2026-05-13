import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileUpdate, ProfileResponse

router = APIRouter()


@router.get("/me/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve los datos del perfil de la usuaria autenticada.
    Incluye: nombre, email, bio, avatar y todas las preferencias.
    """
    return current_user


@router.patch("/me/profile", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sube o cambia la foto de avatar de la usuaria autenticada.
    1. Valida que el archivo sea una imagen.
    2. Lo guarda en uploads/avatars/ con un nombre único.
    3. Actualiza avatar_url de la usuaria en la base de datos.
    4. Devuelve la URL pública del avatar.
    """
    # Solo aceptamos imágenes
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (JPEG, PNG, etc.)",
        )

    # Creamos un nombre único para evitar que dos archivos se llamen igual
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(settings.upload_dir, "avatars", filename)

    # Guardamos el archivo en el disco
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # Actualizamos la URL del avatar en la base de datos
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    await db.commit()

    return {"avatar_url": avatar_url}
