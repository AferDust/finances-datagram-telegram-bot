from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


async def create_user(
    telegram_user_id: int, telegram_user_name: str, session: AsyncSession
):
    instance = User(id=telegram_user_id, username=telegram_user_name)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    return instance
