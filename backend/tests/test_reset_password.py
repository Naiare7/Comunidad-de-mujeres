# Tests de los endpoints de recuperación de contraseña:
#   POST /auth/forgot-password  — Solicitar enlace de recuperación
#   POST /auth/reset-password   — Restablecer la contraseña con el token

import pytest


class TestForgotPassword:
    """Tests del endpoint para solicitar recuperación de contraseña."""

    FORGOT_URL = "/auth/forgot-password"
    REGISTER_URL = "/auth/register"

    # Datos para crear una usuaria de prueba
    REGISTER_PAYLOAD = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }

    @pytest.mark.asyncio
    async def test_forgot_password_existing_email(self, client):
        """
        Solicitar recuperación con un email que SÍ existe en la base de datos.
        El backend siempre devuelve 200 con el mismo mensaje (por seguridad),
        pero internamente genera el token si la usuaria existe.
        """
        # Primero registramos una usuaria para que el email exista
        await client.post(self.REGISTER_URL, json=self.REGISTER_PAYLOAD)

        # Solicitamos recuperación con su email
        response = await client.post(self.FORGOT_URL, json={"email": "test@example.com"})

        assert response.status_code == 200
        data = response.json()
        # El mensaje debe indicar que se enviará un enlace si el email está registrado
        assert "message" in data

    @pytest.mark.asyncio
    async def test_forgot_password_nonexistent_email(self, client):
        """
        Solicitar recuperación con un email que NO existe.
        El backend devuelve EXACTAMENTE el mismo mensaje que cuando existe,
        para no revelar qué emails están registrados (seguridad contra enumeración).
        """
        response = await client.post(
            self.FORGOT_URL, json={"email": "noexiste@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        # El mismo mensaje que cuando el email existe
        assert "message" in data

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email(self, client):
        """
        Enviar un email con formato inválido.
        El validador EmailStr de Pydantic lo rechaza antes de llegar al endpoint.
        """
        response = await client.post(self.FORGOT_URL, json={"email": "esto-no-es-un-email"})

        # 422 = error de validación del schema
        assert response.status_code == 422


class TestResetPassword:
    """Tests del endpoint para restablecer la contraseña con el token."""

    RESET_URL = "/auth/reset-password"
    REGISTER_URL = "/auth/register"
    LOGIN_URL = "/auth/login"

    # Datos para crear una usuaria de prueba
    REGISTER_PAYLOAD = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }

    @pytest.mark.asyncio
    async def test_reset_password_success(self, client):
        """
        Restablecer contraseña con un token VÁLIDO y una nueva contraseña que
        cumple todos los requisitos. Después comprobamos que podemos iniciar
        sesión con la nueva contraseña (la anterior ya no funciona).
        """
        # 1. Registramos una usuaria
        await client.post(self.REGISTER_URL, json=self.REGISTER_PAYLOAD)

        # 2. Creamos un token de recuperación directamente desde el código
        #    (en producción el token se genera en forgot-password y se envía por email)
        from app.core.security import create_reset_token
        token = create_reset_token(data={"sub": "test@example.com"})

        # 3. Restablecemos la contraseña con el token y una nueva contraseña
        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "NewSecure1",
            "confirm_password": "NewSecure1",
        })

        assert response.status_code == 200
        data = response.json()
        assert "restablecida" in data["message"].lower()

        # 4. Verificamos que podemos iniciar sesión con la NUEVA contraseña
        login_response = await client.post(self.LOGIN_URL, json={
            "email": "test@example.com",
            "password": "NewSecure1",
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

        # 5. Verificamos que la CONTRASEÑA ANTERIOR ya no funciona
        old_login_response = await client.post(self.LOGIN_URL, json={
            "email": "test@example.com",
            "password": "SecurePass1",
        })
        assert old_login_response.status_code == 401

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, client):
        """
        Enviar un token que no es un JWT válido.
        El backend debe rechazarlo con error 400.
        """
        response = await client.post(self.RESET_URL, json={
            "token": "este-no-es-un-token-valido",
            "password": "NewSecure1",
            "confirm_password": "NewSecure1",
        })

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_reset_password_weak_password(self, client):
        """
        La nueva contraseña no tiene mayúscula.
        El validador de Pydantic la rechaza (422).
        """
        from app.core.security import create_reset_token
        token = create_reset_token(data={"sub": "test@example.com"})

        # Contraseña sin mayúscula
        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "solominusculas1",
            "confirm_password": "solominusculas1",
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_reset_password_no_number(self, client):
        """
        La nueva contraseña no tiene ningún número.
        El validador de Pydantic la rechaza (422).
        """
        from app.core.security import create_reset_token
        token = create_reset_token(data={"sub": "test@example.com"})

        # Contraseña sin número
        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "OnlyLettersA",
            "confirm_password": "OnlyLettersA",
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_reset_password_too_short(self, client):
        """
        La nueva contraseña tiene menos de 8 caracteres.
        El validador de Pydantic la rechaza (422).
        """
        from app.core.security import create_reset_token
        token = create_reset_token(data={"sub": "test@example.com"})

        # Contraseña demasiado corta (5 caracteres)
        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "Ab1cd",
            "confirm_password": "Ab1cd",
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_reset_password_mismatch(self, client):
        """
        Las dos contraseñas no coinciden.
        El validador de Pydantic las rechaza (422).
        """
        from app.core.security import create_reset_token
        token = create_reset_token(data={"sub": "test@example.com"})

        # password y confirm_password son diferentes
        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "NewSecure1",
            "confirm_password": "Different1",
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_reset_password_nonexistent_user(self, client):
        """
        Token válido pero el email dentro del token no corresponde a ninguna
        usuaria en la base de datos. El backend debe devolver 400.
        """
        from app.core.security import create_reset_token
        # Creamos un token para un email que no existe en la BD
        token = create_reset_token(data={"sub": "noexiste@example.com"})

        response = await client.post(self.RESET_URL, json={
            "token": token,
            "password": "NewSecure1",
            "confirm_password": "NewSecure1",
        })

        assert response.status_code == 400
        assert "no encontrada" in response.json()["detail"].lower()
