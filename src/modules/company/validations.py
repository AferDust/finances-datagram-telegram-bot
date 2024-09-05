from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.company.queries import get_company_by_name_query


def company_creation_validations(name: str):
    if len(name) < 2:
        return False, "Company name is too short. Please enter a valid name."

    if len(name) > 50:
        return False, "Company name is too long. Please enter a shorter name."

    if name.isdigit():
        return False, "Company name should only contain alphanumeric characters."

    return True, "OK"


async def company_exists_validations(name: str, session: AsyncSession):
    existing_company = await session.execute(get_company_by_name_query(name))

    if existing_company.scalar_one_or_none():
        return (
            False,
            "This company name is already taken. Please enter a different name.",
        )

    return True, "OK"
