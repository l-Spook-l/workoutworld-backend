import asyncio
import jwt
import time
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import insert
from src.main import app
from src.users.models import Role
from src.core.database import get_async_session
from src.core.config import DATABASE_URL_TEST
from src.core.config import SECRET_KEY
from src.core.database import Base


engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(bind=engine_test, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")  # создать и удалить бд для тестов
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def test_data():
    return {
        "user_id": 1,
        "workout_id": 0,
        "exercise_id": 0
    }


class BaseTest:
    @staticmethod
    def _generate_jwt_token(user_id: int):
        payload = {
            "sub": str(user_id),
            "aud": ["fastapi-users:auth"],
            "exp": int(time.time()) + 2592000  # 30 days
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def get_headers(self, user_id):
        token = self._generate_jwt_token(user_id=user_id)
        return {"Authorization": f"Bearer {token}"}
