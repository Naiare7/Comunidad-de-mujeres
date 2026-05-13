# Configuración compartida para todos los tests.
# Los "fixtures" de pytest son funciones que preparan el entorno antes de cada test.

import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db


# Usamos SQLite en memoria para los tests: es rápido y no necesita un servidor externo.
# Se crea vacío al empezar y desaparece al terminar.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Reemplaza la base de datos real por la de tests en cada petición."""
    async with test_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Crea un único bucle de eventos para toda la sesión de tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """
    Antes de cada test: crea las tablas.
    Después de cada test: las elimina.
    Así cada test empieza con una base de datos limpia.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """
    Crea un cliente HTTP de prueba que habla directamente con la app
    sin necesitar un servidor real corriendo.
    """
    app.dependency_overrides[get_db] = override_get_db  # Usamos la BD de tests
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()  # Limpiamos los overrides al terminar
