# Tests del endpoint de respuestas (replies).
# 
# TestCreateReply: prueba POST /threads/{thread_id}/replies para crear respuestas.
# TestReplyImages: prueba POST /threads/{thread_id}/replies/{reply_id}/images
#                  para subir imágenes a una respuesta.
#
# Sigue los mismos patrones que los tests de hilos (test_threads.py).

import uuid

import pytest
from sqlalchemy import select

from app.models.forum import Forum, Subforum
from app.models.thread import Thread
from app.models.reply import Reply
from tests.conftest import test_session


class TestCreateReply:
    """
    Tests del endpoint POST /threads/{thread_id}/replies.
    Verifica que se pueda crear una respuesta y que las validaciones
    de permisos, contenido y citas funcionen correctamente.
    """

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

    async def _create_test_thread(self, client, token, forum_id):
        """Crea un hilo de prueba y devuelve su ID."""
        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Hilo para responder",
                "content": "Este hilo tendrá respuestas.",
            },
        )
        data = response.json()
        return data["id"]

    async def _create_test_reply(self, client, token, thread_id, content="Mi respuesta"):
        """Crea una respuesta de prueba y devuelve su ID."""
        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": content},
        )
        data = response.json()
        return data["id"]

    async def _seed_forums(self):
        """Inserta los foros de prueba desde seed.py."""
        from app.seed import FOROS

        async with test_session() as session:
            for foro_data in FOROS:
                forum = Forum(
                    name=foro_data["name"],
                    description=foro_data["description"],
                    icon=foro_data["icon"],
                    display_order=foro_data["display_order"],
                )
                session.add(forum)
                await session.flush()

                for sub_data in foro_data["subforums"]:
                    subforum = Subforum(
                        name=sub_data["name"],
                        description=sub_data["description"],
                        forum_id=forum.id,
                    )
                    session.add(subforum)

            await session.commit()

    async def _get_forum_id(self, name):
        """Devuelve el ID de un foro buscándolo por nombre."""
        async with test_session() as session:
            result = await session.execute(
                select(Forum).where(Forum.name == name)
            )
            forum = result.scalar_one_or_none()
            return forum.id if forum else None

    # ─── Tests ─────────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_create_reply_success(self, client):
        """
        Crea una respuesta en un hilo existente.
        El endpoint debe devolver 201 con los datos de la respuesta creada.
        """
        # 1. Registramos a la usuaria y creamos un foro + hilo
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        assert thread_id is not None

        # 2. Creamos una respuesta en el hilo
        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "¡Qué interesante! Gracias por compartir."},
        )

        assert response.status_code == 201
        data = response.json()

        # Verificamos la estructura de la respuesta devuelta
        assert "id" in data
        assert data["content"] == "¡Qué interesante! Gracias por compartir."
        assert data["author_name"] == "testuser"
        assert data["thread_id"] == thread_id
        assert data["parent_reply_id"] is None
        assert data["is_active"] is True
        assert data["image_urls"] == []
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_reply_with_quote(self, client):
        """
        Crea una respuesta citando a otra respuesta anterior.
        El endpoint debe devolver 201 con el parent_reply_id correcto.
        """
        # 1. Preparamos: usuaria, foro, hilo y primera respuesta
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        # Creamos la primera respuesta (la que vamos a citar)
        first_reply_id = await self._create_test_reply(
            client, token, thread_id, "Esta es la respuesta original"
        )

        # 2. Creamos una segunda respuesta citando a la primera
        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "Estoy de acuerdo con lo que dices.",
                "parent_reply_id": first_reply_id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_reply_id"] == first_reply_id

    @pytest.mark.asyncio
    async def test_create_reply_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.post(
            "/threads/some-id/replies",
            json={"content": "Esto no debería funcionar"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_reply_thread_not_found(self, client):
        """Con un ID de hilo que no existe, el endpoint devuelve 404."""
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/threads/{fake_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Respuesta a un hilo que no existe"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_reply_empty_content(self, client):
        """
        Contenido vacío: el endpoint debe devolver 422 por la validación
        de Pydantic (min_length=1).
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": ""},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_reply_nonexistent_parent(self, client):
        """
        parent_reply_id apunta a una respuesta que no existe.
        El endpoint debe devolver 400.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        fake_reply_id = str(uuid.uuid4())
        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "Citando a alguien que no existe",
                "parent_reply_id": fake_reply_id,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "no existe" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_reply_wrong_thread_parent(self, client):
        """
        parent_reply_id apunta a una respuesta que pertenece a OTRO hilo.
        El endpoint debe devolver 400.
        """
        # 1. Creamos dos hilos en el mismo foro
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_1 = await self._create_test_thread(client, token, forum_id)
        thread_2 = await self._create_test_thread(client, token, forum_id)

        # Creamos una respuesta en el primer hilo
        reply_in_thread_1 = await self._create_test_reply(
            client, token, thread_1, "Respuesta en el hilo 1"
        )

        # 2. Intentamos crear una respuesta en el hilo 2 citando una respuesta del hilo 1
        response = await client.post(
            f"/threads/{thread_2}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "Esto debería fallar",
                "parent_reply_id": reply_in_thread_1,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "no pertenece" in data["detail"].lower()


class TestReplyImages:
    """
    Tests del endpoint POST /threads/{thread_id}/replies/{reply_id}/images.
    Verifica que se puedan subir imágenes a una respuesta y que las
    validaciones de permisos y tipo de archivo funcionen.
    """

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

    async def _create_test_thread(self, client, token, forum_id):
        """Crea un hilo de prueba y devuelve su ID."""
        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Hilo con imágenes en respuestas",
                "content": "Este hilo tendrá respuestas con imágenes.",
            },
        )
        data = response.json()
        return data["id"]

    async def _create_test_reply(self, client, token, thread_id, content="Mi respuesta"):
        """Crea una respuesta de prueba y devuelve su ID."""
        response = await client.post(
            f"/threads/{thread_id}/replies",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": content},
        )
        data = response.json()
        return data["id"]

    async def _seed_forums(self):
        """Inserta los foros de prueba desde seed.py."""
        from app.seed import FOROS

        async with test_session() as session:
            for foro_data in FOROS:
                forum = Forum(
                    name=foro_data["name"],
                    description=foro_data["description"],
                    icon=foro_data["icon"],
                    display_order=foro_data["display_order"],
                )
                session.add(forum)
                await session.flush()

                for sub_data in foro_data["subforums"]:
                    subforum = Subforum(
                        name=sub_data["name"],
                        description=sub_data["description"],
                        forum_id=forum.id,
                    )
                    session.add(subforum)

            await session.commit()

    async def _get_forum_id(self, name):
        """Devuelve el ID de un foro buscándolo por nombre."""
        async with test_session() as session:
            result = await session.execute(
                select(Forum).where(Forum.name == name)
            )
            forum = result.scalar_one_or_none()
            return forum.id if forum else None

    # ─── Tests ─────────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_upload_reply_image_success(self, client):
        """
        Sube una imagen PNG a una respuesta existente.
        El endpoint debe devolver 200 con la URL de la imagen.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        reply_id = await self._create_test_reply(
            client, token, thread_id, "Respuesta con imagen"
        )

        # Creamos un archivo de imagen de prueba (un PNG mínimo de 1x1 píxel)
        image_content = (
            b"\x89PNG\r\n\x1a\n"  # Cabecera PNG
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        response = await client.post(
            f"/threads/{thread_id}/replies/{reply_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.png", image_content, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert data["image_url"].startswith("/uploads/replies/")
        assert data["image_url"].endswith(".png")

    @pytest.mark.asyncio
    async def test_upload_reply_image_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.post(
            "/threads/some-id/replies/other-id/images",
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_upload_reply_image_not_found(self, client):
        """Con un ID de respuesta que no existe, el endpoint devuelve 404."""
        token = await self._register_and_get_token(client)

        fake_thread_id = str(uuid.uuid4())
        fake_reply_id = str(uuid.uuid4())
        response = await client.post(
            f"/threads/{fake_thread_id}/replies/{fake_reply_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrada" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_reply_image_not_author(self, client):
        """
        Una usuaria distinta a la autora de la respuesta intenta subir
        una imagen. El endpoint debe devolver 403.
        """
        # Registramos a la primera usuaria (autora de la respuesta)
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        reply_id = await self._create_test_reply(
            client, token, thread_id, "Respuesta de testuser"
        )

        # Registramos a una segunda usuaria (no es la autora)
        OTHER_PAYLOAD = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        }
        response = await client.post(self.REGISTER_URL, json=OTHER_PAYLOAD)
        other_token = response.json()["access_token"]

        # La segunda usuaria intenta subir una imagen a la respuesta de la primera
        response = await client.post(
            f"/threads/{thread_id}/replies/{reply_id}/images",
            headers={"Authorization": f"Bearer {other_token}"},
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 403
        data = response.json()
        assert "permiso" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_reply_image_invalid_type(self, client):
        """
        Subir un archivo que no es imagen (ej: un .txt).
        El endpoint debe devolver 400.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        reply_id = await self._create_test_reply(
            client, token, thread_id, "Respuesta para probar tipo inválido"
        )

        response = await client.post(
            f"/threads/{thread_id}/replies/{reply_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("not_an_image.txt", b"esto no es una imagen", "text/plain")},
        )

        assert response.status_code == 400
        data = response.json()
        assert "imagen" in data["detail"].lower()
