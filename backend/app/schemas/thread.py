# Esquemas Pydantic para los datos de hilos (threads).
# Definen cómo se ven los hilos cuando los devuelve la API
# y qué datos necesita el endpoint para crear uno nuevo.

from datetime import datetime

from pydantic import BaseModel, Field

# Necesitamos ReplyResponse para devolver las respuestas dentro del detalle del hilo.
from app.schemas.reply import ReplyResponse


class CreateThreadRequest(BaseModel):
    """Datos que la usuaria envía para crear un nuevo hilo."""

    # Título del hilo: obligatorio, entre 3 y 200 caracteres.
    title: str = Field(min_length=3, max_length=200)

    # Contenido del hilo: obligatorio, al menos 1 carácter.
    content: str = Field(min_length=1)

    # Subforo al que pertenece (opcional).
    # Solo se usa cuando el foro tiene subforos (ej: Maternidad > Embarazo).
    # Si el foro no tiene subforos, se deja como None.
    subforum_id: str | None = None


class ThreadResponse(BaseModel):
    """Datos de un hilo que se muestran en el listado."""

    id: str
    title: str
    content: str
    author_id: str
    author_name: str               # Nombre de la autora (se obtiene de la relación)
    forum_id: str | None = None
    subforum_id: str | None = None
    is_active: bool = True

    # Número de respuestas que tiene este hilo.
    # Por ahora siempre es 0 porque aún no existe el modelo Reply.
    # Cuando implementemos HU-10 se calculará con una consulta real.
    reply_count: int = 0

    # Indica si hay actividad nueva desde la última visita de la usuaria.
    # Por ahora es False; se implementará cuando exista el sistema de notificaciones.
    has_new_activity: bool = False

    created_at: datetime
    updated_at: datetime


class ThreadDetailResponse(ThreadResponse):
    """Datos completos de un hilo, incluyendo sus imágenes adjuntas y respuestas."""

    # Lista de URLs de imágenes subidas a este hilo.
    image_urls: list[str] = []

    # Lista de respuestas a este hilo (ordenadas por fecha de creación).
    # Cada respuesta incluye su autora, contenido y metadatos.
    replies: list[ReplyResponse] = []


class PaginatedThreads(BaseModel):
    """Lista de hilos con información de paginación."""

    items: list[ThreadResponse]    # Hilos de la página actual
    total: int                     # Total de hilos en todas las páginas
    page: int                      # Número de página actual
    per_page: int                  # Hilos por página
    pages: int                     # Total de páginas disponibles
