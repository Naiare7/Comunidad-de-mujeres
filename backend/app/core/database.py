# Configuración de la base de datos con SQLAlchemy en modo asíncrono.
# "Asíncrono" significa que las consultas no bloquean el servidor mientras esperan respuesta.

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# El motor es la conexión principal a la base de datos.
# echo=True hace que SQLAlchemy imprima en consola cada consulta SQL que ejecuta (útil para depurar).
engine = create_async_engine(settings.database_url, echo=True)

# La sesión es como una "conversación" con la base de datos.
# Usamos async_sessionmaker para crear sesiones asíncronas.
# expire_on_commit=False evita que los objetos se "olviden" después de guardar.
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Clase base de la que heredan todos los modelos (tablas).
# SQLAlchemy la usa para saber qué tablas existen.
class Base(DeclarativeBase):
    pass


# Función que proporciona una sesión de base de datos a cada endpoint.
# FastAPI la llama automáticamente gracias a Depends(get_db).
# El bloque try/finally garantiza que la sesión siempre se cierre, aunque haya un error.
async def get_db():
    async with async_session() as session:
        try:
            yield session       # Entrega la sesión al endpoint
        finally:
            await session.close()  # Siempre cierra la sesión al terminar


# Crea todas las tablas en la base de datos si no existen todavía.
# Se llama una vez al arrancar el servidor (ver main.py).
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
