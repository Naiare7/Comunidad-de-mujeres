# Modelo de base de datos para Respuestas (Replies) a un hilo.
#
# Una respuesta es un mensaje que una usuaria escribe dentro de un hilo.
# Cada respuesta pertenece a un hilo y tiene una autora.
#
# Una respuesta puede citar a otra respuesta anterior (parent_reply_id).
# Así se implementa la funcionalidad de "citar respuesta" del frontend.
#
# Para borrar una respuesta (HU-11) se usa soft-delete: en lugar de eliminar
# el registro, se marca is_active=False y se reemplaza el contenido.

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reply(Base):
    """Representa una respuesta dentro de un hilo."""

    __tablename__ = "replies"

    # Identificador único universal (UUID) como texto.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Contenido de la respuesta (puede contener markdown básico).
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Clave foránea hacia el hilo al que pertenece esta respuesta.
    thread_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("threads.id"), nullable=False
    )

    # Clave foránea hacia la usuaria que escribió la respuesta.
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Clave foránea hacia otra respuesta (si está citando a alguien).
    # Es opcional (nullable=True). Si es None, la respuesta no cita a nadie.
    parent_reply_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("replies.id"), nullable=True, default=None
    )

    # Soft-delete: en lugar de borrar, se marca como inactiva.
    # El contenido se reemplaza por "Mensaje eliminado" en la HU-11.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Fecha y hora de creación (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Fecha y hora de la última edición (se actualiza al modificar el contenido).
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ─── Relaciones ───────────────────────────────────────────────────────

    # Hilo al que pertenece esta respuesta (muchos-a-uno).
    thread = relationship("Thread", back_populates="replies")

    # Autora de la respuesta (muchos-a-uno).
    author = relationship("User", back_populates="replies")

    # Respuesta a la que cita (autoreferencial).
    # Si una Reply tiene parent_reply_id, aquí está la Reply citada.
    parent_reply = relationship("Reply", back_populates="children", remote_side=[id])

    # Respuestas que citan a esta (lo inverso de parent_reply).
    children = relationship("Reply", back_populates="parent_reply")

    # Imágenes adjuntas a esta respuesta.
    images = relationship("ReplyImage", back_populates="reply", cascade="all, delete-orphan")
