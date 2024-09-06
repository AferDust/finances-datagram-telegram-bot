from sqlalchemy import select

from src.models import Company, MonthlyCompanyData


def get_company_list_query():
    return select(Company.name).join(MonthlyCompanyData).distinct()


def get_company_by_name_query(name: str):
    return select(Company).filter_by(name=name)


def get_monthly_company_information_query(company_id: int, year: int, month: str):
    return select(MonthlyCompanyData).filter_by(
        company_id=company_id, year=year, month=month
    )


def get_all_distinct_years_for_the_user_company_by_id_query(company_id: int):
    return select(MonthlyCompanyData.year).filter_by(company_id=company_id).distinct()


def get_data_for_the_selected_year_and_attribute_query(
    company_id: int, selected_attribute: str, selected_year: int
):
    return (
        select(
            getattr(MonthlyCompanyData, selected_attribute), MonthlyCompanyData.month
        )
        .filter_by(company_id=company_id, year=selected_year)
        .order_by(MonthlyCompanyData.month)
    )
