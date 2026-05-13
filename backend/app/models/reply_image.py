# Modelo de base de datos para imágenes adjuntas a una respuesta.
#
# Cada respuesta puede tener varias imágenes. Se guardan como archivos
# en el servidor y se almacena su URL pública en esta tabla.
# Sigue el mismo patrón que ThreadImage pero para respuestas.

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReplyImage(Base):
    """Representa una imagen adjunta a una respuesta."""

    __tablename__ = "reply_images"

    # Identificador único universal (UUID) como texto.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Clave foránea hacia la respuesta a la que pertenece esta imagen.
    reply_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("replies.id"), nullable=False
    )

    # URL pública de la imagen (ej: /uploads/replies/{uuid}.jpg).
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Fecha y hora de subida (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación inversa: cada imagen pertenece a una respuesta.
    reply = relationship("Reply", back_populates="images")
