from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.models import User


def get_user_query(user_id: int):
    return select(User).options(joinedload(User.company)).filter_by(id=user_id)
