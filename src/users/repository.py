from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


class UserRepository:
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
        query = await session.execute(select(User).filter(User.id == user_id))
        user = query.scalars().first()
        return user
