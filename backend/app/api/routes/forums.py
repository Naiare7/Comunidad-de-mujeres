# Rutas de foros: endpoints para listar foros, ver hilos y crear hilos.
# Solo las usuarias autenticadas pueden acceder.

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.forum import Forum, Subforum
from app.models.thread import Thread
from app.schemas.forum import ForumResponse
from app.schemas.thread import (
    ThreadResponse,
    PaginatedThreads,
    CreateThreadRequest,
)

router = APIRouter()


@router.get("/", response_model=list[ForumResponse])
async def get_forums(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve todos los foros ordenados por su número de orden.
    Cada foro incluye su lista de subforos.
    Requiere estar autenticada (el token JWT se pasa en el header Authorization).
    """
    # Consultamos todos los foros, ordenados por display_order.
    # selectinload le dice a SQLAlchemy que cargue los subforos de cada foro
    # en una consulta separada (más eficiente que cargarlos uno por uno).
    result = await db.execute(
        select(Forum)
        .options(selectinload(Forum.subforums))
        .order_by(Forum.display_order)
    )

    # Extraemos todos los resultados como objetos Forum
    forums = result.scalars().all()

    return forums


@router.get("/{forum_id}/threads", response_model=PaginatedThreads)
async def get_threads(
    forum_id: str,
    page: int = Query(1, ge=1, description="Número de página (empieza en 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Hilos por página"),
    sort: str = Query("recent", pattern="^(recent|comments)$", description="Orden: recent (más recientes) o comments (más comentados)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve los hilos de un foro con paginación y ordenación.
    - Si el foro tiene subforos, busca los hilos de todos sus subforos.
    - Si el foro no tiene subforos, busca los hilos directamente del foro.
    - Solo devuelve hilos activos (no eliminados).
    """
    # 1. Verificamos que el foro exista
    result = await db.execute(
        select(Forum).where(Forum.id == forum_id)
    )
    forum = result.scalar_one_or_none()

    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foro no encontrado",
        )

    # 2. Cargamos los subforos para saber si tiene o no
    result = await db.execute(
        select(Forum)
        .where(Forum.id == forum_id)
        .options(selectinload(Forum.subforums))
    )
    forum = result.scalar_one_or_none()
    has_subforums = len(forum.subforums) > 0

    # 3. Construimos la consulta base de hilos activos
    base_query = select(Thread).where(Thread.is_active == True)

    if has_subforums:
        # Si tiene subforos: hilos que pertenecen a cualquiera de ellos
        subforum_ids = [s.id for s in forum.subforums]
        base_query = base_query.where(Thread.subforum_id.in_(subforum_ids))
    else:
        # Si no tiene subforos: hilos que pertenecen directamente al foro
        base_query = base_query.where(Thread.forum_id == forum_id)

    # 4. Contamos el total de hilos (para la paginación)
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 5. Calculamos las páginas
    pages = math.ceil(total / per_page) if total > 0 else 1

    # 6. Aplicamos ordenación
    if sort == "comments":
        # Por ahora usa updated_at (placeholder hasta HU-10)
        order = Thread.updated_at.desc()
    else:
        # "recent" (por defecto): ordena por última actividad descendente
        order = Thread.updated_at.desc()

    # 7. Consultamos los hilos de la página actual con la autora cargada
    offset = (page - 1) * per_page
    result = await db.execute(
        base_query
        .options(selectinload(Thread.author))
        .order_by(order)
        .offset(offset)
        .limit(per_page)
    )
    threads = result.scalars().all()

    # 8. Convertimos cada hilo a ThreadResponse con el nombre de la autora
    items = []
    for t in threads:
        items.append(
            ThreadResponse(
                id=t.id,
                title=t.title,
                content=t.content,
                author_id=t.author_id,
                author_name=t.author.username,  # Nombre desde la relación cargada
                forum_id=t.forum_id,
                subforum_id=t.subforum_id,
                is_active=t.is_active,
                reply_count=0,
                has_new_activity=False,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )

    # 9. Devolvemos los hilos con metadatos de paginación
    return PaginatedThreads(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.post("/{forum_id}/threads", status_code=status.HTTP_201_CREATED, response_model=ThreadResponse)
async def create_thread(
    forum_id: str,
    thread_data: CreateThreadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea un nuevo hilo en el foro especificado.

    - Si el foro tiene subforos, la usuaria debe indicar en cuál
      quiere crear el hilo (subforum_id).
    - Si el foro no tiene subforos, el hilo se crea directamente
      en el foro (forum_id).

    Requiere estar autenticada.
    """
    # 1. Verificamos que el foro exista
    result = await db.execute(
        select(Forum).where(Forum.id == forum_id)
    )
    forum = result.scalar_one_or_none()

    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foro no encontrado",
        )

    # 2. Cargamos los subforos para saber si tiene o no
    result = await db.execute(
        select(Forum)
        .where(Forum.id == forum_id)
        .options(selectinload(Forum.subforums))
    )
    forum = result.scalar_one_or_none()
    has_subforums = len(forum.subforums) > 0

    # 3. Determinamos si el hilo va al foro o a un subforo
    forum_id_assigned = None
    subforum_id_assigned = None

    if has_subforums:
        # El foro tiene subforos: la usuaria debe elegir uno
        if not thread_data.subforum_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este foro requiere seleccionar un subforo",
            )

        # Verificamos que el subforo indicado pertenezca a este foro
        subforum_ids = [s.id for s in forum.subforums]
        if thread_data.subforum_id not in subforum_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El subforo indicado no pertenece a este foro",
            )

        subforum_id_assigned = thread_data.subforum_id
    else:
        # El foro no tiene subforos: el hilo va directamente al foro
        forum_id_assigned = forum_id

    # 4. Creamos el hilo en la base de datos
    new_thread = Thread(
        title=thread_data.title.strip(),
        content=thread_data.content.strip(),
        author_id=current_user.id,
        forum_id=forum_id_assigned,
        subforum_id=subforum_id_assigned,
    )

    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)

    # 5. Devolvemos el hilo creado como ThreadResponse
    return ThreadResponse(
        id=new_thread.id,
        title=new_thread.title,
        content=new_thread.content,
        author_id=new_thread.author_id,
        author_name=current_user.username,
        forum_id=new_thread.forum_id,
        subforum_id=new_thread.subforum_id,
        is_active=new_thread.is_active,
        reply_count=0,
        has_new_activity=False,
        created_at=new_thread.created_at,
        updated_at=new_thread.updated_at,
    )
