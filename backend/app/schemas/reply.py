# Esquemas Pydantic para los datos de respuestas (replies).
# Definen qué datos necesita el endpoint para crear una respuesta
# y cómo se devuelve al frontend.

from datetime import datetime

from pydantic import BaseModel, Field


class CreateReplyRequest(BaseModel):
    """Datos que la usuaria envía para crear una nueva respuesta."""

    # Contenido de la respuesta: obligatorio, al menos 1 carácter.
    content: str = Field(min_length=1)

    # ID de la respuesta que se está citando (opcional).
    # Si la usuaria hizo clic en "Citar" en una respuesta anterior,
    # este campo contendrá el ID de esa respuesta.
    parent_reply_id: str | None = None


class UpdateReplyRequest(BaseModel):
    """Datos que la usuaria envía para editar el contenido de una respuesta (HU-11)."""

    # Nuevo contenido de la respuesta: obligatorio, al menos 1 carácter.
    content: str = Field(min_length=1)


class ReplyResponse(BaseModel):
    """Datos de una respuesta que se devuelven al frontend."""

    # Identificador único de la respuesta.
    id: str

    # Contenido de la respuesta (puede contener markdown básico).
    content: str

    # ID de la usuaria que escribió la respuesta.
    author_id: str

    # Nombre de la usuaria que escribió la respuesta (se obtiene de la relación).
    author_name: str

    # ID del hilo al que pertenece esta respuesta.
    thread_id: str

    # ID de la respuesta que se está citando (opcional).
    # Si es None, la respuesta no cita a ninguna anterior.
    parent_reply_id: str | None = None

    # Indica si la respuesta está activa (soft-delete, HU-11).
    is_active: bool = True

    # URLs de las imágenes adjuntas a esta respuesta.
    image_urls: list[str] = []

    # Fecha y hora de creación.
    created_at: datetime

    # Fecha y hora de la última edición.
    updated_at: datetime
