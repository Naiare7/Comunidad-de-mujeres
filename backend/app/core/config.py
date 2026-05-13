# Configuración central de la aplicación.
# Pydantic lee automáticamente estas variables desde el archivo .env si existe,
# o usa los valores por defecto que ponemos aquí.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # URL de conexión a la base de datos PostgreSQL
    # Formato: driver://usuario:contraseña@host:puerto/nombre_base_de_datos
    database_url: str = "postgresql+asyncpg://mujeres_user:mujeres_pass@db:5432/mujeres_db"

    # Clave secreta para firmar los tokens JWT. En producción debe ser larga y aleatoria.
    secret_key: str = "super-secret-key-change-in-production"

    # Algoritmo de firma del token JWT
    algorithm: str = "HS256"

    # Cuántos días dura el token antes de expirar
    access_token_expire_days: int = 30

    # Carpeta donde se guardan los archivos subidos (avatares, etc.)
    upload_dir: str = "uploads"

    # Le decimos a Pydantic que busque las variables en el archivo .env
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Creamos una instancia única que se importa en el resto de la app
settings = Settings()
