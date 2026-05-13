# Tests del endpoint de foros (GET /forums).
# Primero se registra una usuaria, se usa su token para autenticarse,
# luego se siembran foros en la base de datos y se prueba el listado.

import pytest
from sqlalchemy import select

from app.models.forum import Forum, Subforum
from app.seed import FOROS
from tests.conftest import test_session


class TestForums:
    FORUMS_URL = "/forums/"
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
        Usa los mismos datos que el script seed.py para que sean coherentes.
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

    @pytest.mark.asyncio
    async def test_get_forums_success(self, client):
        """
        Autenticada y con foros en la base de datos,
        el endpoint devuelve 200 con la lista de foros.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        response = await client.get(
            self.FORUMS_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 8  # Hay 8 foros definidos en FOROS

        # Verificamos la estructura del primer foro
        first = data[0]
        assert "id" in first
        assert first["name"] == "Maternidad"
        assert first["description"] is not None
        assert first["icon"] == "baby"
        assert first["display_order"] == 1
        assert isinstance(first["subforums"], list)
        assert first["thread_count"] == 0
        assert first["last_activity"] is None

    @pytest.mark.asyncio
    async def test_get_forums_unauthorized(self, client):
        """Sin token, el endpoint devuelve 403."""
        response = await client.get(self.FORUMS_URL)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_forums_order(self, client):
        """
        Los foros deben devolverse ordenados por display_order.
        Maternidad (orden 1) primero, Desahogo (orden 8) último.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        response = await client.get(
            self.FORUMS_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verificamos el orden
        assert data[0]["name"] == "Maternidad"
        assert data[1]["name"] == "Viajes"
        assert data[2]["name"] == "Chismes y cotilleos"
        assert data[3]["name"] == "Divorciadas y separadas"
        assert data[4]["name"] == "Mayores de 60 y jubilación"
        assert data[5]["name"] == "Menopausia"
        assert data[6]["name"] == "No maternidad"
        assert data[7]["name"] == "Desahogo y violencia recibida"

        # Verificamos que los display_order sean correlativos
        for i, forum in enumerate(data):
            assert forum["display_order"] == i + 1

    @pytest.mark.asyncio
    async def test_get_forums_includes_subforums(self, client):
        """
        Los foros que tienen subforos deben incluirlos en la respuesta.
        Maternidad tiene 6 subforos; Viajes tiene 0.
        """
        token = await self._register_and_get_token(client)
        await self._seed_forums()

        response = await client.get(
            self.FORUMS_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Maternidad es el primer foro y tiene 6 subforos
        maternidad = data[0]
        assert len(maternidad["subforums"]) == 6
        assert maternidad["subforums"][0]["name"] == "Embarazo"
        assert maternidad["subforums"][1]["name"] == "Muerte perinatal y duelo"
        assert maternidad["subforums"][2]["name"] == "Postparto"
        assert maternidad["subforums"][3]["name"] == "Niños 0-2 años"
        assert maternidad["subforums"][4]["name"] == "Niños 3-6 años"
        assert maternidad["subforums"][5]["name"] == "Adolescencia"

        # Viajes es el segundo foro y no tiene subforos
        viajes = data[1]
        assert len(viajes["subforums"]) == 0
