import logging

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from bot.states import (
    CompanyCreationForm,
    MonthlyCompanyDataForm,
    ViewMonthlyCompanyDataForm,
    RetrieveCompanyDataForm,
)
from src.modules.company.validations import (
    company_creation_validations,
    company_exists_validations,
)
from src.modules.company.services import (
    create_company,
    delete_company,
    get_company_list,
    get_all_distinct_years_for_the_user_company_by_id,
)

router = Router()


def generate_list_of_buttons_based_on_list(keyboards_list):
    keyboard = []
    for value in keyboards_list:
        keyboard.append([KeyboardButton(text=str(value))])

    keyboard.append([KeyboardButton(text="Exit")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def generate_list_of_buttons_based_on_enum(keyboards_enum):
    keyboard = []
    for month in keyboards_enum:
        keyboard.append([KeyboardButton(text=str(month.value))])

    keyboard.append([KeyboardButton(text="Exit")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def get_company_exists_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="View Company")],
            [KeyboardButton(text="Add Information")],
            [KeyboardButton(text="Delete Company")],
            [KeyboardButton(text="Exit")],
        ],
        resize_keyboard=True,
    )


async def get_company_not_exists_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Company")],
            [KeyboardButton(text="Exit")],
        ],
        resize_keyboard=True,
    )


async def send_company_options(user: User, message: types.Message):
    if user.company:
        kb = await get_company_exists_buttons()
        await message.answer("Choose an option for your company:", reply_markup=kb)
    else:
        kb = await get_company_not_exists_buttons()
        await message.answer(
            "You don't have a company yet. You can create one:", reply_markup=kb
        )


@router.message(lambda message: message.text == "List of Companies")
async def list_of_companies_handler(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    companies = await get_company_list(session)

    if not companies:
        await message.answer("No companies available.")
        return

    companies_keyboard = generate_list_of_buttons_based_on_list(companies)
    await message.answer("Please select a company:", reply_markup=companies_keyboard)

    await state.set_state(RetrieveCompanyDataForm.name)


@router.message(lambda message: message.text == "Create Company")
async def create_company_command_handler(
    message: types.Message, state: FSMContext, user: User
):
    logging.info("In Company create action")
    logging.info(f"User company exists validation: {user.company}")
    if user.company:
        await message.answer("You already have company!")
        return

    await message.answer(
        "Please enter the name of your new company:", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CompanyCreationForm.name)


@router.message(StateFilter(CompanyCreationForm.name))
async def create_company_command_state_handler(
    message: types.Message, state: FSMContext, user: User, session: AsyncSession
):
    logging.info("In 'create_company_command_state_handler' function")
    kb = await get_company_exists_buttons()

    try:
        company_name = message.text
        logging.info(f"Company name {company_name}")

        is_valid, content = company_creation_validations(company_name)
        logging.info(f"Company name validation: {is_valid}")
        if not is_valid:
            await message.answer(content)
            return

        is_valid, content = await company_exists_validations(company_name, session)
        logging.info(f"Company exists validation: {is_valid}")
        if not is_valid:
            await message.answer(content)
            return

        instance = await create_company(user.id, company_name, session)
        await message.answer(
            f"Company '{instance.name}' has been created!", reply_markup=kb
        )
        await state.clear()
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(lambda message: message.text == "Delete Company")
async def delete_company_handler(
    message: types.Message, user: User, session: AsyncSession
):
    logging.info("In 'handle_delete_company' function")
    kb = await get_company_not_exists_buttons()

    try:
        if user and user.company:
            content = await delete_company(user.company, session)
            await message.answer(content, reply_markup=kb)
        else:
            await message.answer("You don't have a company to delete.", reply_markup=kb)
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception), reply_markup=kb)


@router.message(lambda message: message.text == "Add Information")
async def add_information_handler(
    message: types.Message, state: FSMContext, user: User
):
    if not user.company:
        await message.answer("You don't have a company to add information to.")
        return

    await message.answer(
        "Please enter the year for the data:", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(MonthlyCompanyDataForm.year)


@router.message(lambda message: message.text == "View Company")
async def view_user_company_handler(
    message: types.Message, state: FSMContext, user: User, session: AsyncSession
):
    if not user.company:
        await message.answer("You don't have a company.")
        return

    years = await get_all_distinct_years_for_the_user_company_by_id(
        user.company.id, session
    )

    if not years:
        await message.answer("No data available for your company.")
        return

    years_keyboard = generate_list_of_buttons_based_on_list(years)
    await message.answer("Please select a year:", reply_markup=years_keyboard)
    await state.set_state(ViewMonthlyCompanyDataForm.year)
