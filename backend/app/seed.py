# Script para poblar la base de datos con los foros y subforos iniciales.
#
# Uso: python -m app.seed
#
# Es seguro ejecutarlo varias veces: si ya existen foros, no los duplica.

import asyncio

from sqlalchemy import select

from app.core.database import engine, async_session, Base
from app.models.forum import Forum, Subforum


# Datos de los 8 foros principales con sus subforos.
# Cada foro tiene: nombre, descripción, icono de Lucide y orden de visualización.
FOROS = [
    {
        "name": "Maternidad",
        "description": "Espacio para compartir experiencias sobre la maternidad en todas sus etapas.",
        "icon": "baby",
        "display_order": 1,
        "subforums": [
            {"name": "Embarazo", "description": "Todo sobre el embarazo: cuidados, dudas y experiencias."},
            {"name": "Muerte perinatal y duelo", "description": "Espacio seguro para compartir y acompañar en la pérdida."},
            {"name": "Postparto", "description": "Recuperación, lactancia y los primeros meses con el bebé."},
            {"name": "Niños 0-2 años", "description": "Crianza de bebés y niños pequeños."},
            {"name": "Niños 3-6 años", "description": "Educación infantil, juegos y desarrollo."},
            {"name": "Adolescencia", "description": "Cómo acompañar a hijas e hijos en la adolescencia."},
        ],
    },
    {
        "name": "Viajes",
        "description": "Recomendaciones, experiencias y planes de viaje entre mujeres.",
        "icon": "plane",
        "display_order": 2,
        "subforums": [],
    },
    {
        "name": "Chismes y cotilleos",
        "description": "El rincón para hablar de todo un poco sin filtros.",
        "icon": "message-circle",
        "display_order": 3,
        "subforums": [],
    },
    {
        "name": "Divorciadas y separadas",
        "description": "Apoyo mutuo para quienes están pasando por una separación o divorcio.",
        "icon": "heart-crack",
        "display_order": 4,
        "subforums": [],
    },
    {
        "name": "Mayores de 60 y jubilación",
        "description": "Espacio para mujeres mayores de 60: ocio, salud y nuevos proyectos.",
        "icon": "sun",
        "display_order": 5,
        "subforums": [],
    },
    {
        "name": "Menopausia",
        "description": "Información, cuidados y experiencias compartidas sobre la menopausia.",
        "icon": "thermometer",
        "display_order": 6,
        "subforums": [],
    },
    {
        "name": "No maternidad",
        "description": "Para mujeres que han elegido no ser madres o no han podido serlo.",
        "icon": "heart",
        "display_order": 7,
        "subforums": [],
    },
    {
        "name": "Desahogo y violencia recibida",
        "description": "Espacio confidencial para desahogarse y recibir apoyo en situaciones de violencia.",
        "icon": "shield",
        "display_order": 8,
        "subforums": [],
    },
]


async def seed():
    """
    Crea los foros y subforos en la base de datos si no existen todavía.
    Es seguro ejecutarlo múltiples veces (verifica duplicados por nombre).
    """
    # 1. Creamos las tablas por si no se han creado aún
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Abrimos una sesión para trabajar con los datos
    async with async_session() as session:
        # 3. Verificamos si ya hay foros (para no duplicar)
        result = await session.execute(select(Forum))
        existing_forums = result.scalars().all()

        if existing_forums:
            print(f"Ya existen {len(existing_forums)} foros. No se añaden duplicados.")
            return

        # 4. Recorremos la lista de foros y los creamos
        for foro_data in FOROS:
            forum = Forum(
                name=foro_data["name"],
                description=foro_data["description"],
                icon=foro_data["icon"],
                display_order=foro_data["display_order"],
            )
            session.add(forum)
            # Forzamos el flush para que forum.id esté disponible
            await session.flush()

            # 5. Creamos los subforos de cada foro
            for sub_data in foro_data["subforums"]:
                subforum = Subforum(
                    name=sub_data["name"],
                    description=sub_data["description"],
                    forum_id=forum.id,
                )
                session.add(subforum)

        # 6. Guardamos todo en la base de datos
        await session.commit()
        print("¡Foros y subforos creados correctamente!")


if __name__ == "__main__":
    asyncio.run(seed())
