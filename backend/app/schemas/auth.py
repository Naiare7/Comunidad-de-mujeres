# Schemas de Pydantic para validar los datos que entran y salen de la API.
# Pydantic comprueba automáticamente que los datos tienen el formato correcto
# antes de que lleguen a nuestra lógica de negocio.

import re
from datetime import datetime

from pydantic import BaseModel, field_validator, EmailStr


class UserCreate(BaseModel):
    """Datos que la usuaria envía al registrarse."""
    username: str
    email: EmailStr       # EmailStr valida automáticamente que sea un email válido
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, value: str) -> str:
        """El nombre de usuario debe tener al menos 3 caracteres."""
        if len(value.strip()) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres")
        return value.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """La contraseña debe ser segura: mínimo 8 caracteres, una mayúscula y un número."""
        if len(value) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe contener al menos un número")
        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        """Las dos contraseñas deben ser iguales."""
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return value


class ResetPasswordRequest(BaseModel):
    """Datos que la usuaria envía para restablecer su contraseña con el token."""
    token: str
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """La contraseña debe ser segura: mínimo 8 caracteres, una mayúscula y un número."""
        if len(value) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe contener al menos un número")
        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        """Las dos contraseñas deben ser iguales."""
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return value


class ForgotPasswordRequest(BaseModel):
    """Datos que la usuaria envía para solicitar recuperación de contraseña."""
    email: EmailStr


class LoginRequest(BaseModel):
    """Datos que la usuaria envía al iniciar sesión."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Datos de la usuaria que devolvemos en las respuestas (sin contraseña)."""
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    # from_attributes=True permite crear este schema desde un objeto SQLAlchemy (el modelo User)
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Respuesta completa del login/registro: token + datos de la usuaria."""
    access_token: str
    token_type: str = "bearer"  # Tipo estándar de token en APIs REST
    user: UserResponse
