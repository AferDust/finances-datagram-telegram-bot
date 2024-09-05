from sqlalchemy import select

from src.models import Company


def get_company_by_name_query(name: str):
    return select(Company).filter_by(name=name)
