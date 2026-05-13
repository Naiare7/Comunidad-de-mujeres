# Modelo de base de datos para Hilos (Threads) de conversación.
#
# Un hilo es un tema de conversación creado por una usuaria dentro de un foro
# o subforo. Otros hilos se crean como respuestas dentro de este hilo.
#
# Un hilo puede pertenecer:
#   - Directamente a un foro (si el foro no tiene subforos, ej: "Viajes")
#   - A un subforo (si el foro tiene subforos, ej: "Maternidad > Embarazo")
# En ambos casos, forum_id o subforum_id se rellena según corresponda.

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Thread(Base):
    """Representa un hilo de conversación en un foro o subforo."""

    __tablename__ = "threads"

    # Identificador único universal (UUID) como texto.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Título del hilo (visible en el listado de hilos).
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Contenido del mensaje principal del hilo.
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Clave foránea hacia la usuaria que creó el hilo.
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Foro al que pertenece el hilo (si el foro no tiene subforos).
    forum_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("forums.id"), nullable=True, default=None
    )

    # Subforo al que pertenece el hilo (si el foro tiene subforos).
    subforum_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("subforums.id"), nullable=True, default=None
    )

    # Soft-delete: en lugar de borrar hilos, se marcan como inactivos.
    # El contenido se reemplaza por "Mensaje eliminado" en la HU-11.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Fecha y hora de creación (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Fecha y hora de la última actividad (se actualiza al crear o responder).
    # Sirve para ordenar los hilos por "más recientes".
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ─── Relaciones ───────────────────────────────────────────────────────

    # Autora del hilo (relación muchos-a-uno con User).
    author = relationship("User", back_populates="threads")

    # Foro al que pertenece (si aplica).
    forum = relationship("Forum", back_populates="threads")

    # Subforo al que pertenece (si aplica).
    subforum = relationship("Subforum", back_populates="threads")

    # Imágenes adjuntas a este hilo.
    images = relationship("ThreadImage", back_populates="thread", cascade="all, delete-orphan")

    # Respuestas a este hilo (ordenadas por fecha de creación).
    replies = relationship("Reply", back_populates="thread", cascade="all, delete-orphan")
