from aiogram.fsm.state import State, StatesGroup


class CompanyCreationForm(StatesGroup):
    name = State()


class MonthlyCompanyDataForm(StatesGroup):
    year = State()
    month = State()
    income = State()
    expenses = State()
    profit = State()
    kpn = State()


class ViewMonthlyCompanyDataForm(StatesGroup):
    year = State()
    field = State()


class RetrieveCompanyDataForm(StatesGroup):
    name = State()
    id = State()
    year = State()
    field = State()
