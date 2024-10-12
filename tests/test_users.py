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


async def test_register_user(ac: AsyncClient):
    # Данные для регистрации
    user_data = {
        "email": "user1@example.com",
        "first_name": "User1_first name",
        "password": "password_test",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "last_name": "User1_last name",
        "phone": "0123456789"
    }

    response = await ac.post("/api/users/register", json=user_data)

    assert response.status_code == 201

    async with async_session_maker() as session:
        query = select(User).where(User.email == user_data["email"])
        result = await session.execute(query)
        registered_user = result.scalar()
        assert registered_user is not None, "Пользователь не найден в базе данных."

        assert registered_user.id == 1
        assert registered_user.role_id == 2, "Не верная роль"
        assert registered_user.email == user_data["email"], "Email не совпадает."
        assert registered_user.first_name == user_data["first_name"], "Имя не совпадает."
        assert registered_user.last_name == user_data["last_name"], "Фамилия не совпадает."
        assert registered_user.phone == user_data["phone"], "Телефон не совпадает."
        assert registered_user.is_superuser == user_data["is_superuser"], "Статус суперпользователя не совпадает."
        assert registered_user.is_active == user_data["is_active"], "Статус активности не совпадает."
