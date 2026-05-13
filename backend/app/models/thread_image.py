# Modelo de base de datos para imágenes adjuntas a un hilo.
#
# Cada hilo puede tener varias imágenes. Se guardan como archivos
# en el servidor y se almacena su URL pública en esta tabla.
#
# Por ahora las imágenes se suben una a una tras crear el hilo.
# En el futuro se podrían subir varias a la vez.

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ThreadImage(Base):
    """Representa una imagen adjunta a un hilo."""

    __tablename__ = "thread_images"

    # Identificador único universal (UUID) como texto.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Clave foránea hacia el hilo al que pertenece esta imagen.
    thread_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("threads.id"), nullable=False
    )

    # URL pública de la imagen (ej: /uploads/threads/{uuid}.jpg).
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Fecha y hora de subida (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación inversa: cada imagen pertenece a un hilo.
    thread = relationship("Thread", back_populates="images")
