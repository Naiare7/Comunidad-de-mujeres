# Rutas de hilos: endpoints para ver detalle de un hilo y subir imágenes adjuntas.
# Solo las usuarias autenticadas pueden acceder.

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.thread import Thread
from app.models.thread_image import ThreadImage
from app.models.reply import Reply
from app.models.reply_image import ReplyImage
from app.schemas.thread import ThreadDetailResponse, UpdateThreadRequest
from app.schemas.reply import CreateReplyRequest, ReplyResponse, UpdateReplyRequest

router = APIRouter()

# Carpeta donde se guardan las imágenes de los hilos
THREAD_UPLOAD_DIR = os.path.join(settings.upload_dir, "threads")

# Carpeta donde se guardan las imágenes de las respuestas
REPLIES_UPLOAD_DIR = os.path.join(settings.upload_dir, "replies")


@router.get("/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread_detail(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve los datos completos de un hilo, incluyendo sus imágenes adjuntas.

    - Busca el hilo por su ID.
    - Carga la autora y las imágenes relacionadas.
    - Devuelve el título, contenido, autora, fecha e image_urls.
    """
    # Buscamos el hilo con la autora, las imágenes y las respuestas cargadas
    result = await db.execute(
        select(Thread)
        .where(Thread.id == thread_id)
        .options(
            selectinload(Thread.author),
            selectinload(Thread.images),
            selectinload(Thread.replies).selectinload(Reply.author),
            selectinload(Thread.replies).selectinload(Reply.images),
        )
    )
    thread = result.scalar_one_or_none()

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # Solo mostramos hilos activos
    if not thread.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # Extraemos las URLs de las imágenes ordenadas por fecha de subida
    image_urls = [img.image_url for img in sorted(
        thread.images, key=lambda x: x.created_at
    )]

    # Construimos las respuestas ordenadas por fecha de creación (más antigua primero)
    replies_sorted = sorted(thread.replies, key=lambda r: r.created_at)
    replies_response = [
        ReplyResponse(
            id=reply.id,
            content=reply.content,
            author_id=reply.author_id,
            author_name=reply.author.username,
            thread_id=reply.thread_id,
            parent_reply_id=reply.parent_reply_id,
            is_active=reply.is_active,
            image_urls=[img.image_url for img in sorted(
                reply.images, key=lambda x: x.created_at
            )],
            created_at=reply.created_at,
            updated_at=reply.updated_at,
        )
        for reply in replies_sorted
        if reply.is_active  # Solo mostramos respuestas activas
    ]

    return ThreadDetailResponse(
        id=thread.id,
        title=thread.title,
        content=thread.content,
        author_id=thread.author_id,
        author_name=thread.author.username,
        forum_id=thread.forum_id,
        subforum_id=thread.subforum_id,
        is_active=thread.is_active,
        reply_count=len(replies_response),
        has_new_activity=False,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        image_urls=image_urls,
        replies=replies_response,
    )


@router.patch("/{thread_id}", response_model=ThreadDetailResponse)
async def update_thread(
    thread_id: str,
    update_data: UpdateThreadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edita el contenido de un hilo (HU-11, Tarea 2).

    - Solo la autora del hilo puede editar su contenido.
    - Se actualiza el campo 'content' con el nuevo texto.
    - 'updated_at' se actualiza automáticamente gracias al modelo.
    - Devuelve el hilo completo con todos sus datos.
    """
    # 1. Buscamos el hilo en la base de datos
    result = await db.execute(
        select(Thread)
        .where(Thread.id == thread_id)
        .options(
            selectinload(Thread.author),
            selectinload(Thread.images),
            selectinload(Thread.replies).selectinload(Reply.author),
            selectinload(Thread.replies).selectinload(Reply.images),
        )
    )
    thread = result.scalar_one_or_none()

    # Si el hilo no existe, devolvemos 404
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # Solo mostramos hilos activos
    if not thread.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # 2. Solo la autora puede editar el hilo
    if thread.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este hilo",
        )

    # 3. Actualizamos el contenido del hilo
    thread.content = update_data.content.strip()

    # Guardamos los cambios en la base de datos
    await db.commit()
    await db.refresh(thread)

    # 4. Construimos la respuesta igual que en get_thread_detail
    image_urls = [img.image_url for img in sorted(
        thread.images, key=lambda x: x.created_at
    )]

    replies_sorted = sorted(thread.replies, key=lambda r: r.created_at)
    replies_response = [
        ReplyResponse(
            id=reply.id,
            content=reply.content,
            author_id=reply.author_id,
            author_name=reply.author.username,
            thread_id=reply.thread_id,
            parent_reply_id=reply.parent_reply_id,
            is_active=reply.is_active,
            image_urls=[img.image_url for img in sorted(
                reply.images, key=lambda x: x.created_at
            )],
            created_at=reply.created_at,
            updated_at=reply.updated_at,
        )
        for reply in replies_sorted
        if reply.is_active
    ]

    return ThreadDetailResponse(
        id=thread.id,
        title=thread.title,
        content=thread.content,
        author_id=thread.author_id,
        author_name=thread.author.username,
        forum_id=thread.forum_id,
        subforum_id=thread.subforum_id,
        is_active=thread.is_active,
        reply_count=len(replies_response),
        has_new_activity=False,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        image_urls=image_urls,
        replies=replies_response,
    )


@router.post("/{thread_id}/images")
async def upload_thread_image(
    thread_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sube una imagen adjunta a un hilo.

    - Solo la autora del hilo puede subir imágenes.
    - Solo acepta archivos de imagen (JPEG, PNG, etc.).
    - Las imágenes se guardan en uploads/threads/ con un nombre único.
    - Devuelve la URL pública de la imagen subida.
    """
    # 1. Buscamos el hilo en la base de datos
    result = await db.execute(
        select(Thread).where(Thread.id == thread_id)
    )
    thread = result.scalar_one_or_none()

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # 2. Solo la autora del hilo puede subir imágenes
    if thread.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para subir imágenes a este hilo",
        )

    # 3. Validamos que el archivo sea una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (JPEG, PNG, etc.)",
        )

    # 4. Aseguramos que la carpeta de destino exista
    os.makedirs(THREAD_UPLOAD_DIR, exist_ok=True)

    # 5. Creamos un nombre único para el archivo
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(THREAD_UPLOAD_DIR, filename)

    # 6. Guardamos el archivo en el disco
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # 7. Guardamos la referencia en la base de datos
    image_url = f"/uploads/threads/{filename}"
    thread_image = ThreadImage(
        thread_id=thread_id,
        image_url=image_url,
    )
    db.add(thread_image)
    await db.commit()

    return {"image_url": image_url}


@router.post("/{thread_id}/replies", status_code=status.HTTP_201_CREATED, response_model=ReplyResponse)
async def create_reply(
    thread_id: str,
    reply_data: CreateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva respuesta en un hilo.

    - Busca el hilo por su ID y verifica que exista y esté activo.
    - Si la usuaria está citando una respuesta anterior (parent_reply_id),
      verifica que esa respuesta exista y pertenezca al mismo hilo.
    - Guarda la respuesta en la base de datos y la devuelve.
    """
    # 1. Buscamos el hilo en la base de datos
    result = await db.execute(
        select(Thread).where(Thread.id == thread_id)
    )
    thread = result.scalar_one_or_none()

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # Solo permitimos responder en hilos activos
    if not thread.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # 2. Si la usuaria está citando una respuesta anterior, verificamos que exista
    if reply_data.parent_reply_id:
        result = await db.execute(
            select(Reply).where(Reply.id == reply_data.parent_reply_id)
        )
        parent_reply = result.scalar_one_or_none()

        if parent_reply is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La respuesta que intentas citar no existe",
            )

        # La respuesta citada debe pertenecer al mismo hilo
        if parent_reply.thread_id != thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La respuesta que intentas citar no pertenece a este hilo",
            )

    # 3. Creamos la respuesta en la base de datos
    new_reply = Reply(
        content=reply_data.content.strip(),
        thread_id=thread_id,
        author_id=current_user.id,
        parent_reply_id=reply_data.parent_reply_id,
    )

    db.add(new_reply)
    await db.commit()
    await db.refresh(new_reply)

    # 4. Cargamos la autora para obtener su nombre de usuaria
    result = await db.execute(
        select(Reply)
        .where(Reply.id == new_reply.id)
        .options(selectinload(Reply.author))
    )
    new_reply = result.scalar_one_or_none()

    # 5. Devolvemos la respuesta creada
    return ReplyResponse(
        id=new_reply.id,
        content=new_reply.content,
        author_id=new_reply.author_id,
        author_name=new_reply.author.username,
        thread_id=new_reply.thread_id,
        parent_reply_id=new_reply.parent_reply_id,
        is_active=new_reply.is_active,
        image_urls=[],
        created_at=new_reply.created_at,
        updated_at=new_reply.updated_at,
    )


@router.post("/{thread_id}/replies/{reply_id}/images")
async def upload_reply_image(
    thread_id: str,
    reply_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sube una imagen adjunta a una respuesta.

    - Solo la autora de la respuesta puede subir imágenes.
    - Solo acepta archivos de imagen (JPEG, PNG, etc.).
    - Las imágenes se guardan en uploads/replies/ con un nombre único.
    - Devuelve la URL pública de la imagen subida.
    """
    # 1. Buscamos la respuesta en la base de datos
    result = await db.execute(
        select(Reply).where(Reply.id == reply_id)
    )
    reply = result.scalar_one_or_none()

    if reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respuesta no encontrada",
        )

    # 2. Solo la autora de la respuesta puede subir imágenes
    if reply.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para subir imágenes a esta respuesta",
        )

    # 3. Validamos que el archivo sea una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (JPEG, PNG, etc.)",
        )

    # 4. Aseguramos que la carpeta de destino exista
    os.makedirs(REPLIES_UPLOAD_DIR, exist_ok=True)

    # 5. Creamos un nombre único para el archivo
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(REPLIES_UPLOAD_DIR, filename)

    # 6. Guardamos el archivo en el disco
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # 7. Guardamos la referencia en la base de datos
    image_url = f"/uploads/replies/{filename}"
    reply_image = ReplyImage(
        reply_id=reply_id,
        image_url=image_url,
    )
    db.add(reply_image)
    await db.commit()

    return {"image_url": image_url}


@router.patch("/{thread_id}/replies/{reply_id}", response_model=ReplyResponse)
async def update_reply(
    thread_id: str,
    reply_id: str,
    update_data: UpdateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edita el contenido de una respuesta (HU-11, Tarea 2).

    - Solo la autora de la respuesta puede editar su contenido.
    - Se actualiza el campo 'content' con el nuevo texto.
    - 'updated_at' se actualiza automáticamente gracias al modelo.
    - Devuelve la respuesta con todos sus datos.
    """
    # 1. Buscamos la respuesta en la base de datos
    result = await db.execute(
        select(Reply)
        .where(Reply.id == reply_id, Reply.thread_id == thread_id)
        .options(selectinload(Reply.author), selectinload(Reply.images))
    )
    reply = result.scalar_one_or_none()

    # Si la respuesta no existe, devolvemos 404
    if reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respuesta no encontrada",
        )

    # Solo mostramos respuestas activas
    if not reply.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respuesta no encontrada",
        )

    # 2. Solo la autora puede editar la respuesta
    if reply.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar esta respuesta",
        )

    # 3. Actualizamos el contenido de la respuesta
    reply.content = update_data.content.strip()

    # Guardamos los cambios en la base de datos
    await db.commit()
    await db.refresh(reply)

    # 4. Devolvemos la respuesta actualizada
    return ReplyResponse(
        id=reply.id,
        content=reply.content,
        author_id=reply.author_id,
        author_name=reply.author.username,
        thread_id=reply.thread_id,
        parent_reply_id=reply.parent_reply_id,
        is_active=reply.is_active,
        image_urls=[img.image_url for img in sorted(
            reply.images, key=lambda x: x.created_at
        )],
        created_at=reply.created_at,
        updated_at=reply.updated_at,
    )


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina (soft-delete) un hilo (HU-11, Tarea 4).

    - Solo la autora del hilo puede eliminarlo.
    - En lugar de borrar el registro, se marca como inactivo (is_active = False)
      y se reemplaza el contenido por "Mensaje eliminado".
    - El título, la autora y las fechas se conservan para contexto.
    """
    # 1. Buscamos el hilo en la base de datos
    result = await db.execute(
        select(Thread).where(Thread.id == thread_id)
    )
    thread = result.scalar_one_or_none()

    # Si el hilo no existe, devolvemos 404
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # Si ya estaba eliminado, también devolvemos 404
    if not thread.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hilo no encontrado",
        )

    # 2. Solo la autora puede eliminar el hilo
    if thread.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este hilo",
        )

    # 3. Soft-delete: marcamos como inactivo y reemplazamos el contenido
    thread.is_active = False
    thread.content = "Mensaje eliminado"

    # Guardamos los cambios en la base de datos
    await db.commit()

    # 4. Devolvemos un mensaje de confirmación
    return {"mensaje": "Hilo eliminado"}


@router.delete("/{thread_id}/replies/{reply_id}")
async def delete_reply(
    thread_id: str,
    reply_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina (soft-delete) una respuesta (HU-11, Tarea 4).

    - Solo la autora de la respuesta puede eliminarla.
    - En lugar de borrar el registro, se marca como inactiva (is_active = False)
      y se reemplaza el contenido por "Mensaje eliminado".
    - La autora y las fechas se conservan para contexto.
    """
    # 1. Buscamos la respuesta en la base de datos
    result = await db.execute(
        select(Reply).where(Reply.id == reply_id, Reply.thread_id == thread_id)
    )
    reply = result.scalar_one_or_none()

    # Si la respuesta no existe, devolvemos 404
    if reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respuesta no encontrada",
        )

    # Si ya estaba eliminada, también devolvemos 404
    if not reply.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respuesta no encontrada",
        )

    # 2. Solo la autora puede eliminar la respuesta
    if reply.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta respuesta",
        )

    # 3. Soft-delete: marcamos como inactiva y reemplazamos el contenido
    reply.is_active = False
    reply.content = "Mensaje eliminado"

    # Guardamos los cambios en la base de datos
    await db.commit()

    # 4. Devolvemos un mensaje de confirmación
    return {"mensaje": "Respuesta eliminada"}
