# Modelos de base de datos para Foros y Subforos.
#
# Un Foro (Forum) tiene varios Subforos (Subforum).
# Por ejemplo: el foro "Maternidad" tiene subforos "Embarazo", "Postparto", etc.

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Forum(Base):
    """Representa un foro principal (categoría)."""

    __tablename__ = "forums"

    # Identificador único universal (UUID) como texto.
    # Se genera automáticamente al crear un nuevo foro.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Nombre del foro, por ejemplo "Maternidad" o "Viajes".
    # Es único para no tener dos foros con el mismo nombre.
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Descripción breve que explica de qué trata el foro.
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    # Nombre del icono de Lucide que representa este foro.
    # Por ejemplo: "baby" para Maternidad, "plane" para Viajes.
    icon: Mapped[str] = mapped_column(String(50), nullable=True, default=None)

    # Número de orden para mostrar los foros en el listado.
    # El foro con display_order=1 aparece primero.
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Fecha y hora en que se creó el foro (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación: un foro tiene muchos subforos.
    # cascade="all, delete-orphan" significa que si se borra un foro,
    # también se borran todos sus subforos automáticamente.
    subforums = relationship("Subforum", back_populates="forum", cascade="all, delete-orphan")

    # Hilos creados directamente en este foro (cuando no tiene subforos).
    threads = relationship("Thread", back_populates="forum")


class Subforum(Base):
    """Representa un subforo dentro de un foro principal."""

    __tablename__ = "subforums"

    # Identificador único universal (UUID) como texto.
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Nombre del subforo, por ejemplo "Embarazo" o "Postparto".
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Descripción breve del subforo.
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    # Clave foránea: el ID del foro al que pertenece este subforo.
    # ForeignKey("forums.id") crea una relación a nivel de base de datos.
    forum_id: Mapped[str] = mapped_column(String(36), ForeignKey("forums.id"), nullable=False)

    # Fecha y hora de creación (en UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación inversa: cada subforo pertenece a un foro.
    # back_populates conecta con el atributo "subforums" del modelo Forum.
    forum = relationship("Forum", back_populates="subforums")

    # Hilos creados dentro de este subforo.
    threads = relationship("Thread", back_populates="subforum")
