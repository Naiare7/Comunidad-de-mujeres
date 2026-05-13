# Esquemas Pydantic para los datos de foros y subforos.
# Definen cómo se ven los datos cuando los devuelve la API.

from pydantic import BaseModel


class SubforumResponse(BaseModel):
    """Datos de un subforo que se muestran en el listado."""

    id: str
    name: str
    description: str | None = None

    # Número de hilos de conversación en este subforo.
    # Por ahora siempre es 0 porque aún no existe el modelo Thread.
    # Cuando implementemos HU-08 se calculará con una consulta real.
    thread_count: int = 0

    # Fecha del último mensaje escrito en este subforo.
    # Por ahora es None; se poblará cuando existan hilos y respuestas.
    last_activity: str | None = None

    # Le decimos a Pydantic que puede crear este schema desde un objeto SQLAlchemy
    model_config = {"from_attributes": True}


class ForumResponse(BaseModel):
    """Datos de un foro principal que se muestran en el listado."""

    id: str
    name: str
    description: str | None = None
    icon: str | None = None
    display_order: int

    # Lista de subforos que pertenecen a este foro.
    # SQLAlchemy los cargará automáticamente gracias a la relación.
    subforums: list[SubforumResponse] = []

    # Número total de hilos en todo el foro (suma de sus subforos).
    # Por ahora siempre es 0 (igual que en SubforumResponse).
    thread_count: int = 0

    # Fecha del último mensaje en cualquier subforo de este foro.
    last_activity: str | None = None

    model_config = {"from_attributes": True}
