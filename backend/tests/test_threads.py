# Tests del endpoint de hilos (GET /forums/{forum_id}/threads).
# Primero se registra una usuaria, se siembran foros y hilos en la base de datos,
# y luego se prueba el listado paginado de hilos.

import uuid

import pytest
from sqlalchemy import select

from app.models.forum import Forum, Subforum
from app.models.thread import Thread
from app.models.user import User
from app.seed import FOROS
from tests.conftest import test_session


class TestThreads:
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

    async def _seed_forums(self):
        """
        Inserta los foros y subforos de prueba en la base de datos.
        Usa los mismos datos que el script seed.py.
        """
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

    async def _get_user_id(self):
        """Devuelve el ID de la usuaria de prueba."""
        async with test_session() as session:
            result = await session.execute(
                select(User).where(User.username == "testuser")
            )
            user = result.scalar_one_or_none()
            return user.id if user else None

    async def _seed_threads(self, count, author_id, forum_id):
        """
        Crea 'count' hilos de prueba en el foro indicado.
        Cada hilo tiene un título único y contenido de prueba.
        """
        async with test_session() as session:
            for i in range(count):
                thread = Thread(
                    title=f"Hilo de prueba {i + 1}",
                    content=f"Este es el contenido del hilo número {i + 1}.",
                    author_id=author_id,
                    forum_id=forum_id,
                )
                session.add(thread)

            await session.commit()

    @pytest.mark.asyncio
    async def test_get_threads_success(self, client):
        """
        Con foros seedeados y un hilo creado, el endpoint devuelve 200
        con la lista de hilos y la estructura correcta.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        # Obtenemos el ID del foro "Viajes" (no tiene subforos)
        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        # Obtenemos el ID de la usuaria creada
        author_id = await self._get_user_id()
        assert author_id is not None

        # Creamos 1 hilo de prueba en el foro Viajes
        await self._seed_threads(1, author_id, forum_id)

        # Consultamos los hilos
        response = await client.get(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["per_page"] == 20
        assert data["pages"] == 1

        # Verificamos la estructura del hilo devuelto
        thread = data["items"][0]
        assert "id" in thread
        assert thread["title"] == "Hilo de prueba 1"
        assert thread["content"] == "Este es el contenido del hilo número 1."
        assert thread["author_id"] == author_id
        assert thread["author_name"] == "testuser"
        assert thread["forum_id"] == forum_id
        assert thread["subforum_id"] is None
        assert thread["is_active"] is True
        assert thread["reply_count"] == 0
        assert thread["has_new_activity"] is False
        assert "created_at" in thread
        assert "updated_at" in thread

    @pytest.mark.asyncio
    async def test_get_threads_empty(self, client):
        """
        Foro existente pero sin hilos: el endpoint devuelve 200
        con la lista vacía y total = 0.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        response = await client.get(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 20
        assert data["pages"] == 1

    @pytest.mark.asyncio
    async def test_get_threads_unauthorized(self, client):
        """Sin token, el endpoint devuelve 403."""
        response = await client.get("/forums/some-id/threads")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_threads_not_found(self, client):
        """Con un ID de foro que no existe, el endpoint devuelve 404."""
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/forums/{fake_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_threads_pagination(self, client):
        """
        Con 25 hilos y per_page=20, la página 1 debe tener 20 hilos,
        la página 2 debe tener 5, y el total debe ser 25.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        author_id = await self._get_user_id()

        # Creamos 25 hilos de prueba
        await self._seed_threads(25, author_id, forum_id)

        # Página 1: debe tener 20 hilos
        response = await client.get(
            f"/forums/{forum_id}/threads?page=1&per_page=20",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 20
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["pages"] == 2

        # Página 2: debe tener los 5 hilos restantes
        response = await client.get(
            f"/forums/{forum_id}/threads?page=2&per_page=20",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 25
        assert data["page"] == 2
        assert data["pages"] == 2


class TestCreateThread:
    """
    Tests del endpoint POST /forums/{forum_id}/threads.
    Verifica que se pueda crear un hilo y que las validaciones funcionen.
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

    async def _seed_forums(self):
        """
        Inserta los foros y subforos de prueba en la base de datos,
        igual que en TestThreads.
        """
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

    async def _get_subforum_id(self, forum_id, name):
        """Devuelve el ID de un subforo dentro de un foro."""
        async with test_session() as session:
            result = await session.execute(
                select(Subforum).where(
                    Subforum.forum_id == forum_id,
                    Subforum.name == name,
                )
            )
            subforum = result.scalar_one_or_none()
            return subforum.id if subforum else None

    # ─── Tests ─────────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_create_thread_success(self, client):
        """
        Crea un hilo en un foro sin subforos (Viajes).
        El endpoint debe devolver 201 con los datos del hilo creado.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        # "Viajes" no tiene subforos → el hilo va directo al foro
        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Mi primer viaje sola",
                "content": "Quiero compartir mi experiencia viajando sola por primera vez.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Mi primer viaje sola"
        assert data["content"] == "Quiero compartir mi experiencia viajando sola por primera vez."
        assert data["forum_id"] == forum_id
        assert data["subforum_id"] is None
        assert data["author_name"] == "testuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_thread_with_subforum(self, client):
        """
        Crea un hilo en un foro CON subforos (Maternidad > Embarazo).
        El hilo debe quedar asociado al subforo.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Maternidad")
        assert forum_id is not None

        subforum_id = await self._get_subforum_id(forum_id, "Embarazo")
        assert subforum_id is not None

        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Primer trimestre",
                "content": "¿Alguien más tiene náuseas en el primer trimestre?",
                "subforum_id": subforum_id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Primer trimestre"
        assert data["subforum_id"] == subforum_id
        assert data["forum_id"] is None  # No va directo al foro, va al subforo

    @pytest.mark.asyncio
    async def test_create_thread_missing_subforum(self, client):
        """
        Foro con subforos (Maternidad) pero sin subforum_id en la petición.
        El endpoint debe devolver 400.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Maternidad")
        assert forum_id is not None

        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Hilo sin subforo",
                "content": "Esto debería fallar porque Maternidad tiene subforos.",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "subforo" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_thread_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.post(
            "/forums/some-id/threads",
            json={"title": "Test", "content": "Test content"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_thread_forum_not_found(self, client):
        """Con un ID de foro que no existe, el endpoint debe devolver 404."""
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/forums/{fake_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test", "content": "Test content"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_thread_invalid_data(self, client):
        """
        Título vacío: el endpoint debe devolver 422 por la validación
        de Pydantic (min_length=3).
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        response = await client.post(
            f"/forums/{forum_id}/threads",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "", "content": "Test content"},
        )

        assert response.status_code == 422


class TestThreadImages:
    """
    Tests del endpoint POST /threads/{thread_id}/images.
    Verifica que se puedan subir imágenes a un hilo y que las
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
                "title": "Hilo con imágenes",
                "content": "Este hilo tendrá imágenes adjuntas.",
            },
        )
        data = response.json()
        return data["id"]

    @pytest.mark.asyncio
    async def test_upload_image_success(self, client):
        """
        Sube una imagen PNG a un hilo existente.
        El endpoint debe devolver 200 con la URL de la imagen.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        assert thread_id is not None

        # Creamos un archivo de imagen de prueba (un PNG mínimo de 1x1 píxel)
        image_content = (
            b"\x89PNG\r\n\x1a\n"  # Cabecera PNG
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        response = await client.post(
            f"/threads/{thread_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.png", image_content, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert data["image_url"].startswith("/uploads/threads/")
        assert data["image_url"].endswith(".png")

    @pytest.mark.asyncio
    async def test_upload_image_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.post(
            "/threads/some-id/images",
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_upload_image_thread_not_found(self, client):
        """Con un ID de hilo que no existe, el endpoint devuelve 404."""
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/threads/{fake_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_image_not_author(self, client):
        """
        Una usuaria distinta a la autora del hilo intenta subir una imagen.
        El endpoint debe devolver 403.
        """
        # Registramos a la primera usuaria (autora del hilo)
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        # Registramos a una segunda usuaria (no es la autora)
        OTHER_PAYLOAD = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        }
        response = await client.post(self.REGISTER_URL, json=OTHER_PAYLOAD)
        other_token = response.json()["access_token"]

        # La segunda usuaria intenta subir una imagen al hilo de la primera
        response = await client.post(
            f"/threads/{thread_id}/images",
            headers={"Authorization": f"Bearer {other_token}"},
            files={"file": ("test.png", b"fake", "image/png")},
        )

        assert response.status_code == 403
        data = response.json()
        assert "permiso" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_image_invalid_type(self, client):
        """
        Subir un archivo que no es imagen (ej: un .txt).
        El endpoint debe devolver 400.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        response = await client.post(
            f"/threads/{thread_id}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("not_an_image.txt", b"esto no es una imagen", "text/plain")},
        )

        assert response.status_code == 400
        data = response.json()
        assert "imagen" in data["detail"].lower()

    # ─── Helpers ─────────────────────────────────────────────────────────

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


class TestThreadDetail:
    """
    Tests del endpoint GET /threads/{thread_id}.
    Verifica que se pueda obtener el detalle de un hilo con sus imágenes.
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
                "title": "Hilo de detalle",
                "content": "Contenido del hilo para probar el detalle.",
            },
        )
        data = response.json()
        return data["id"]

    @pytest.mark.asyncio
    async def test_get_thread_detail_success(self, client):
        """
        Hilo existente: el endpoint devuelve 200 con los datos completos,
        incluyendo el título, contenido, autora y fecha.
        """
        token = await self._register_and_get_token(client)

        # Creamos un foro y un hilo de prueba
        async with test_session() as session:
            forum = Forum(name="Test Forum", icon="heart", display_order=1)
            session.add(forum)
            await session.commit()
            forum_id = forum.id

        thread_id = await self._create_test_thread(client, token, forum_id)

        # Consultamos el detalle del hilo
        response = await client.get(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == thread_id
        assert data["title"] == "Hilo de detalle"
        assert data["content"] == "Contenido del hilo para probar el detalle."
        assert data["author_name"] == "testuser"
        assert data["image_urls"] == []
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_get_thread_detail_not_found(self, client):
        """Hilo que no existe: el endpoint devuelve 404."""
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/threads/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_thread_detail_unauthorized(self, client):
        """Sin token, el endpoint devuelve 403."""
        response = await client.get("/threads/some-id")

        assert response.status_code == 403


class TestUpdateThread:
    """
    Tests del endpoint PATCH /threads/{thread_id} (HU-11, Tarea 2).
    Verifica que solo la autora pueda editar el contenido de un hilo.
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
                "title": "Hilo para editar",
                "content": "Contenido original del hilo.",
            },
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
    async def test_update_thread_success(self, client):
        """
        Editar el contenido de un hilo propio.
        El endpoint debe devolver 200 con el contenido actualizado.
        """
        # 1. Preparamos: foro, usuaria e hilo
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        assert thread_id is not None

        # 2. Editamos el contenido del hilo
        nuevo_contenido = "Este es el contenido editado del hilo."
        response = await client.patch(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": nuevo_contenido},
        )

        # 3. Verificamos que la respuesta sea correcta
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == nuevo_contenido
        assert data["title"] == "Hilo para editar"
        assert data["author_name"] == "testuser"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_update_thread_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.patch(
            "/threads/some-id",
            json={"content": "Nuevo contenido"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_thread_not_found(self, client):
        """Con un ID de hilo que no existe, el endpoint devuelve 404."""
        import uuid
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.patch(
            f"/threads/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Nuevo contenido"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_thread_not_author(self, client):
        """
        Una usuaria distinta a la autora intenta editar el hilo.
        El endpoint debe devolver 403.
        """
        # 1. Registramos a la primera usuaria (autora del hilo)
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        # 2. Registramos a una segunda usuaria (no es la autora)
        OTHER_PAYLOAD = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        }
        response = await client.post(self.REGISTER_URL, json=OTHER_PAYLOAD)
        other_token = response.json()["access_token"]

        # 3. La segunda usuaria intenta editar el hilo de la primera
        response = await client.patch(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"content": "Intento de edición ajena"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "permiso" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_thread_empty_content(self, client):
        """
        Contenido vacío: el endpoint debe devolver 422 por la validación
        de Pydantic (min_length=1).
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        response = await client.patch(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": ""},
        )

        assert response.status_code == 422


class TestDeleteThread:
    """
    Tests del endpoint DELETE /threads/{thread_id} (HU-11, Tarea 4).
    Verifica que solo la autora pueda eliminar (soft-delete) un hilo
    y que el contenido se reemplace por "Mensaje eliminado".
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
                "title": "Hilo para eliminar",
                "content": "Contenido del hilo que se va a eliminar.",
            },
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
    async def test_delete_thread_success(self, client):
        """
        Eliminar un hilo propio.
        El endpoint devuelve 200 y el hilo queda marcado como inactivo
        con el contenido reemplazado por "Mensaje eliminado" en la BD.
        """
        # 1. Preparamos: foro, usuaria e hilo
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)
        assert thread_id is not None

        # 2. Eliminamos el hilo
        response = await client.delete(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # 3. Verificamos la respuesta
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "eliminado" in data["mensaje"].lower()

        # 4. Verificamos directamente en la BD que el soft-delete funcionó
        async with test_session() as session:
            result = await session.execute(
                select(Thread).where(Thread.id == thread_id)
            )
            thread = result.scalar_one()
            assert thread.is_active is False
            assert thread.content == "Mensaje eliminado"
            # El título se conserva para dar contexto
            assert thread.title == "Hilo para eliminar"

    @pytest.mark.asyncio
    async def test_delete_thread_unauthorized(self, client):
        """Sin token, el endpoint debe devolver 403."""
        response = await client.delete("/threads/some-id")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_thread_not_found(self, client):
        """Con un ID de hilo que no existe, el endpoint devuelve 404."""
        import uuid
        token = await self._register_and_get_token(client)

        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/threads/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_thread_not_author(self, client):
        """
        Una usuaria distinta a la autora intenta eliminar el hilo.
        El endpoint debe devolver 403.
        """
        # 1. Registramos a la primera usuaria (autora del hilo)
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        # 2. Registramos a una segunda usuaria (no es la autora)
        OTHER_PAYLOAD = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        }
        response = await client.post(self.REGISTER_URL, json=OTHER_PAYLOAD)
        other_token = response.json()["access_token"]

        # 3. La segunda usuaria intenta eliminar el hilo de la primera
        response = await client.delete(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "permiso" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_thread_already_deleted(self, client):
        """
        Intentar eliminar un hilo que ya fue eliminado.
        El endpoint debe devolver 404.
        """
        # 1. Preparamos y eliminamos el hilo una vez
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        forum_id = await self._get_forum_id("Viajes")
        assert forum_id is not None

        thread_id = await self._create_test_thread(client, token, forum_id)

        # Primera eliminación: debe funcionar
        response = await client.delete(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # 2. Intentamos eliminar el mismo hilo otra vez
        response = await client.delete(
            f"/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
