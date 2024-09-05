from aiogram import BaseMiddleware
from sqlalchemy.orm import session

from src.modules.user.services import create_user
from src.modules.user.queries import get_user_query
from src.database import get_db_session


class SessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async for session in get_db_session():
            data["session"] = session
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        session = data.get("session", None)

        if hasattr(event, "from_user") and session:
            user_id = event.from_user.id
            user_result = await session.execute(get_user_query(user_id))
            user = user_result.scalar_one_or_none()

            if user is None:
                user = await create_user(user_id, event.from_user.full_name, session)

            data["user"] = user
            return await handler(event, data)


session_middleware = SessionMiddleware()
user_middleware = UserMiddleware()
