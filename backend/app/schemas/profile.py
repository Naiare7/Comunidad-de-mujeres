from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    hobbies: list[str] | None = None
    age_range: str | None = None
    life_situations: list[str] | None = None
    city: str | None = None
    province: str | None = None
    radius: int | None = None
    bio: str | None = None
    avatar_url: str | None = None
    visibility: dict | None = None


class ProfileResponse(BaseModel):
    """Datos completos del perfil que se muestran en la página de perfil."""
    username: str
    email: str
    bio: str | None
    avatar_url: str | None
    hobbies: list[str]
    age_range: str | None
    life_situations: list[str]
    city: str | None
    province: str | None
    radius: int | None
    visibility: dict

    model_config = {"from_attributes": True}
