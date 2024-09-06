from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.company.services import get_or_none_company_by_name
from src.models import MonthEnum


def company_creation_validations(name: str):
    if len(name) < 2:
        return False, "Company name is too short. Please enter a valid name."

    if len(name) > 50:
        return False, "Company name is too long. Please enter a shorter name."

    if name.isdigit():
        return False, "Company name should only contain alphanumeric characters."

    return True, "OK"


async def company_exists_validations(name: str, session: AsyncSession):
    existing_company = await get_or_none_company_by_name(name, session)

    if existing_company:
        return (
            False,
            "This company name is already taken. Please enter a different name.",
        )

    return True, "OK"


def company_information_year_validation(year: int):
    if year < 1900 or year > 2100:
        return False, "Please enter a valid year between 1900 and 2100."
    return True, "OK"


def company_information_month_validation(month: str):
    if month not in [m.value for m in MonthEnum]:
        return False, "Please select a valid month from the options provided."
    return True, "OK"


def company_information_field_positive_validation(
    attribute_first: int, attribute_second: str
):
    if attribute_first < 0:
        return False, f"{attribute_second} must be a positive integer."
    return True, "OK"
