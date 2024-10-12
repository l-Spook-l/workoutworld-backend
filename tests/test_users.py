from sqlalchemy import insert, select
from httpx import AsyncClient
from src.users.models import Role, User
from .conftest import async_session_maker, generate_jwt_token


async def test_roles():
    async with async_session_maker() as session:
        stmt = insert(Role).values(id=1, name="admin")
        await session.execute(stmt)
        await session.commit()

        stmt = insert(Role).values(id=2, name="user")
        await session.execute(stmt)
        await session.commit()

        query = select(Role.id, Role.name)
        result = await session.execute(query)

        assert result.all() == [(1, 'admin'), (2, 'user')], "Роли не добавились"
