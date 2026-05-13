# Tests del endpoint de registro (/auth/register).
# Cada test comprueba un caso diferente: éxito, errores de validación, duplicados...

import pytest


class TestRegister:
    REGISTER_URL = "/auth/register"

    # Datos válidos que usamos como base en varios tests
    VALID_PAYLOAD = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """El registro con datos correctos devuelve 201 y un token JWT."""
        response = await client.post(self.REGISTER_URL, json=self.VALID_PAYLOAD)

        assert response.status_code == 201
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
        assert "id" in data["user"]
        assert data["user"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """No se puede registrar dos usuarias con el mismo email."""
        await client.post(self.REGISTER_URL, json=self.VALID_PAYLOAD)

        payload = {**self.VALID_PAYLOAD, "username": "otheruser"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 409
        assert "email" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        """No se puede registrar dos usuarias con el mismo nombre de usuario."""
        await client.post(self.REGISTER_URL, json=self.VALID_PAYLOAD)

        payload = {**self.VALID_PAYLOAD, "email": "other@example.com"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 409
        assert "usuario" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Un email con formato incorrecto devuelve error 422 (validación)."""
        payload = {**self.VALID_PAYLOAD, "email": "not-an-email"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Una contraseña demasiado corta devuelve error 422."""
        payload = {**self.VALID_PAYLOAD, "password": "short", "confirm_password": "short"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_password_no_uppercase(self, client):
        """Una contraseña sin mayúsculas devuelve error 422."""
        payload = {**self.VALID_PAYLOAD, "password": "longenough1", "confirm_password": "longenough1"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_password_no_number(self, client):
        """Una contraseña sin números devuelve error 422."""
        payload = {**self.VALID_PAYLOAD, "password": "LongEnough", "confirm_password": "LongEnough"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_passwords_mismatch(self, client):
        """Si las dos contraseñas no coinciden, devuelve error 422."""
        payload = {**self.VALID_PAYLOAD, "confirm_password": "DifferentPass1"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_username(self, client):
        """Un nombre de usuario con menos de 3 caracteres devuelve error 422."""
        payload = {**self.VALID_PAYLOAD, "username": "ab"}
        response = await client.post(self.REGISTER_URL, json=payload)

        assert response.status_code == 422


class TestLogin:
    """Tests del endpoint de inicio de sesión (/auth/login)."""

    LOGIN_URL = "/auth/login"
    REGISTER_URL = "/auth/register"

    # Datos de una usuaria que creamos antes de cada test de login
    REGISTER_PAYLOAD = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Login con credenciales correctas devuelve 200 y un token JWT."""
        # Primero registramos una usuaria para tenerla en la base de datos
        await client.post(self.REGISTER_URL, json=self.REGISTER_PAYLOAD)

        # Ahora hacemos login con el mismo email y contraseña
        payload = {"email": "test@example.com", "password": "SecurePass1"}
        response = await client.post(self.LOGIN_URL, json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client):
        """Login con un email que no existe en la base de datos devuelve 401."""
        payload = {"email": "noexiste@example.com", "password": "SecurePass1"}
        response = await client.post(self.LOGIN_URL, json=payload)

        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        """Login con la contraseña incorrecta devuelve 401."""
        # Registramos una usuaria
        await client.post(self.REGISTER_URL, json=self.REGISTER_PAYLOAD)

        # Hacemos login con la contraseña equivocada
        payload = {"email": "test@example.com", "password": "WrongPass1"}
        response = await client.post(self.LOGIN_URL, json=payload)

        assert response.status_code == 401
        assert "incorrectos" in response.json()["detail"].lower()
