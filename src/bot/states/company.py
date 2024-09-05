from aiogram.fsm.state import State, StatesGroup


class CompanyCreationForm(StatesGroup):
    name = State()
