# Tests del endpoint de perfil (/users/me/profile).
# Primero se registra una usuaria, se usa su token para autenticarse,
# y luego se prueba el PATCH de perfil.

import pytest


class TestProfile:
    PROFILE_URL = "/users/me/profile"
    REGISTER_URL = "/auth/register"

    REGISTER_PAYLOAD = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }

    async def _register_and_get_token(self, client):
        """Crea una usuaria y devuelve su token JWT."""
        response = await client.post(self.REGISTER_URL, json=self.REGISTER_PAYLOAD)
        data = response.json()
        return data["access_token"]

    @pytest.mark.asyncio
    async def test_update_profile_hobbies_only(self, client):
        """Actualizar solo las aficiones devuelve 200 y las aficiones guardadas."""
        token = await self._register_and_get_token(client)

        payload = {"hobbies": ["viajar", "lectura"]}
        response = await client.patch(
            self.PROFILE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hobbies"] == ["viajar", "lectura"]
        assert data["age_range"] is None
        assert data["life_situations"] == []

    @pytest.mark.asyncio
    async def test_update_profile_all_fields(self, client):
        """Actualizar todos los campos del perfil devuelve 200 con los datos completos."""
        token = await self._register_and_get_token(client)

        payload = {
            "hobbies": ["viajar", "cine", "pintura"],
            "age_range": "26-35",
            "life_situations": ["madre_primeriza", "nueva_en_la_ciudad"],
            "city": "Madrid",
            "province": "28",
            "radius": 50,
        }
        response = await client.patch(
            self.PROFILE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hobbies"] == ["viajar", "cine", "pintura"]
        assert data["age_range"] == "26-35"
        assert data["life_situations"] == ["madre_primeriza", "nueva_en_la_ciudad"]
        assert data["city"] == "Madrid"
        assert data["province"] == "28"
        assert data["radius"] == 50

    @pytest.mark.asyncio
    async def test_update_profile_partial(self, client):
        """Actualizar solo un campo no altera los demás."""
        token = await self._register_and_get_token(client)

        payload1 = {"hobbies": ["viajar"], "age_range": "36-45"}
        await client.patch(
            self.PROFILE_URL,
            json=payload1,
            headers={"Authorization": f"Bearer {token}"},
        )

        payload2 = {"city": "Barcelona"}
        response = await client.patch(
            self.PROFILE_URL,
            json=payload2,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hobbies"] == ["viajar"]
        assert data["age_range"] == "36-45"
        assert data["city"] == "Barcelona"

    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client):
        """Sin token, el endpoint devuelve 401."""
        payload = {"hobbies": ["viajar"]}
        response = await client.patch(self.PROFILE_URL, json=payload)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_bio(self, client):
        """
        Actualizar solo la biografía.
        El endpoint devuelve 200 con la bio guardada y el resto de campos intactos.
        """
        token = await self._register_and_get_token(client)

        payload = {"bio": "Soy una mujer apasionada por la lectura y el cine"}
        response = await client.patch(
            self.PROFILE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Soy una mujer apasionada por la lectura y el cine"
        # Verificamos que también devuelve los campos básicos de la usuaria
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_update_visibility(self, client):
        """
        Actualizar la configuración de visibilidad de los campos del perfil.
        El endpoint devuelve 200 con la visibilidad guardada.
        """
        token = await self._register_and_get_token(client)

        payload = {
            "visibility": {
                "bio": "private",
                "hobbies": "public",
                "age_range": "private",
                "life_situations": "public",
                "location": "private",
            }
        }
        response = await client.patch(
            self.PROFILE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["visibility"]["bio"] == "private"
        assert data["visibility"]["hobbies"] == "public"
        assert data["visibility"]["age_range"] == "private"
        assert data["visibility"]["life_situations"] == "public"
        assert data["visibility"]["location"] == "private"

    @pytest.mark.asyncio
    async def test_update_bio_and_visibility(self, client):
        """
        Actualizar la bio y la visibilidad en una misma llamada.
        Ambos campos deben guardarse correctamente a la vez.
        """
        token = await self._register_and_get_token(client)

        payload = {
            "bio": "Nueva biografía con visibilidad privada",
            "visibility": {"bio": "private", "hobbies": "public"},
        }
        response = await client.patch(
            self.PROFILE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Nueva biografía con visibilidad privada"
        assert data["visibility"]["bio"] == "private"
        assert data["visibility"]["hobbies"] == "public"

    @pytest.mark.asyncio
    async def test_get_profile(self, client):
        """
        Obtener el perfil completo con un token válido.
        Devuelve 200 con todos los campos del perfil.
        """
        token = await self._register_and_get_token(client)

        response = await client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # Campos básicos de la usuaria
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        # Campos del perfil (deben existir aunque estén vacíos)
        assert "bio" in data
        assert "avatar_url" in data
        assert "hobbies" in data
        assert "age_range" in data
        assert "life_situations" in data
        assert "city" in data
        assert "province" in data
        assert "radius" in data
        assert "visibility" in data

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client):
        """Obtener el perfil sin token devuelve 403."""
        response = await client.get(self.PROFILE_URL)

        assert response.status_code == 403
