from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Company, MonthlyCompanyData
from src.modules.company.queries import (
    get_monthly_company_information_query,
    get_all_distinct_years_for_the_user_company_by_id_query,
    get_data_for_the_selected_year_and_attribute_query,
    get_company_list_query,
    get_company_by_name_query,
)


async def get_or_none_company_by_name(company_name: str, session: AsyncSession):
    instance = await session.execute(get_company_by_name_query(company_name))
    return instance.scalar_one_or_none()


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


async def create_or_update_monthly_company_information_instance(
    data, company: Company, session: AsyncSession
):
    year = data["year"]
    month = data["month"]
    income = data["income"]
    expenses = data["expenses"]
    profit = data["profit"]
    kpn = data["kpn"]

    instance = await session.execute(
        get_monthly_company_information_query(company.id, year, month)
    )
    instance = instance.scalar_one_or_none()

    if instance:
        instance.income = income
        instance.expenses = expenses
        instance.profit = profit
        instance.kpn = kpn
    else:
        instance = MonthlyCompanyData(
            company_id=company.id,
            year=data["year"],
            month=data["month"],
            income=data["income"],
            expenses=data["expenses"],
            profit=data["profit"],
            kpn=data["kpn"],
        )
        session.add(instance)

    await session.commit()
    await session.refresh(instance)
    return instance


async def get_company_list(session: AsyncSession):
    result = await session.execute(get_company_list_query())
    return result.scalars().all()


async def get_all_distinct_years_for_the_user_company_by_id(
    company_id: int, session: AsyncSession
):
    result = await session.execute(
        get_all_distinct_years_for_the_user_company_by_id_query(company_id)
    )
    return result.scalars().all()


async def get_data_for_the_selected_year_and_attribute(
    company_id: int, selected_field: str, selected_year: int, session: AsyncSession
):
    results = await session.execute(
        get_data_for_the_selected_year_and_attribute_query(
            company_id, selected_field, selected_year
        )
    )
    return results.all()
