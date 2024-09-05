from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Company


async def create_company(user_id: int, company_name: str, session: AsyncSession):
    instance = Company(name=company_name, user_id=user_id)

    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    return instance


async def delete_company(company: Company, session: AsyncSession):
    await session.delete(company)
    await session.commit()

    return "Company has been deleted."
