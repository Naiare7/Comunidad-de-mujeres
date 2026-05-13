import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.core.config import settings
from app.api.routes import auth, profile, forums, threads


# Crear la carpeta de uploads al importar (necesario para StaticFiles)
os.makedirs(settings.upload_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear las subcarpetas de archivos subidos si no existen
    os.makedirs(os.path.join(settings.upload_dir, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "threads"), exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="Comunidad de Mujeres API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (avatares subidos) desde la carpeta uploads/
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/users", tags=["users"])
app.include_router(forums.router, prefix="/forums", tags=["forums"])
app.include_router(threads.router, prefix="/threads", tags=["threads"])
