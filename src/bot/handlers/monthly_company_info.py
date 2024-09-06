import io
import logging

import matplotlib.pyplot as plt

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    BufferedInputFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.handlers.company import (
    get_company_exists_buttons,
    generate_list_of_buttons_based_on_enum,
    generate_list_of_buttons_based_on_list,
)
from src.models import User, MonthEnum
from src.bot.states.company import (
    MonthlyCompanyDataForm,
    ViewMonthlyCompanyDataForm,
    RetrieveCompanyDataForm,
)
from src.modules.company.validations import (
    company_information_year_validation,
    company_information_month_validation,
    company_information_field_positive_validation,
)
from src.modules.company.services import (
    create_or_update_monthly_company_information_instance,
    get_data_for_the_selected_year_and_attribute,
    get_all_distinct_years_for_the_user_company_by_id,
    get_or_none_company_by_name,
)

router = Router()


def generate_monthly_data_chart_based_on_company_records(
    records, selected_field, selected_year
):
    values = [record[0] for record in records]
    months = [record[1] for record in records]

    plt.figure(figsize=(10, 6))
    plt.bar(months, values, color="blue")
    plt.xlabel("MONTH")
    plt.ylabel(selected_field.upper())
    plt.title(f"{selected_field.upper()} for {selected_year}")

    image_stream = io.BytesIO()
    plt.savefig(image_stream, format="png")
    image_stream.seek(0)
    plt.close()

    return image_stream


def get_monthly_company_information_attributes_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Income"), KeyboardButton(text="Expenses")],
            [KeyboardButton(text="Profit"), KeyboardButton(text="KPN")],
            [KeyboardButton(text="Exit")],
        ],
        resize_keyboard=True,
    )


@router.message(StateFilter(MonthlyCompanyDataForm.year))
async def handle_year_input(message: types.Message, state: FSMContext):
    try:
        year = int(message.text)

        is_valid, content = company_information_year_validation(year)
        if not is_valid:
            await message.answer(content)
            return

        await state.update_data(year=year)

        month_keyboard = generate_list_of_buttons_based_on_enum(MonthEnum)
        await message.answer("Please select the month:", reply_markup=month_keyboard)
        await state.set_state(MonthlyCompanyDataForm.month)
    except ValueError as value_error:
        logging.error(str(value_error))
        await message.answer("Please enter a valid year.")
    except Exception as exception:
        await message.answer(str(exception))


@router.message(StateFilter(MonthlyCompanyDataForm.month))
async def handle_month_input(message: types.Message, state: FSMContext):
    month = message.text

    is_valid, content = company_information_month_validation(month)
    if not is_valid:
        await message.answer(content)
        return

    await state.update_data(month=month)
    await message.answer(
        "Please enter the company's income for this month:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(MonthlyCompanyDataForm.income)


@router.message(StateFilter(MonthlyCompanyDataForm.income))
async def handle_income_input(message: types.Message, state: FSMContext):
    try:
        income = int(message.text)

        is_valid, content = company_information_field_positive_validation(
            income, "income"
        )
        if not is_valid:
            await message.answer(content)
            return

        await state.update_data(income=income)

        await message.answer("Please enter the company's expenses for this month:")
        await state.set_state(MonthlyCompanyDataForm.expenses)
    except ValueError:
        await message.answer("Please enter a valid integer for income.")
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(StateFilter(MonthlyCompanyDataForm.expenses))
async def handle_expenses_input(message: types.Message, state: FSMContext):
    try:
        expenses = int(message.text)

        is_valid, content = company_information_field_positive_validation(
            expenses, "expenses"
        )
        if not is_valid:
            await message.answer(content)
            return

        await state.update_data(expenses=expenses)

        await message.answer("Please enter the company's profit for this month:")
        await state.set_state(MonthlyCompanyDataForm.profit)
    except ValueError:
        await message.answer("Please enter a valid integer for expenses.")
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(StateFilter(MonthlyCompanyDataForm.profit))
async def handle_profit_input(message: types.Message, state: FSMContext):
    try:
        profit = int(message.text)

        is_valid, content = company_information_field_positive_validation(
            profit, "profit"
        )
        if not is_valid:
            await message.answer(content)
            return

        await state.update_data(profit=profit)

        await message.answer("Please enter the company's KPN (tax) for this month:")
        await state.set_state(MonthlyCompanyDataForm.kpn)
    except ValueError:
        await message.answer("Please enter a valid integer for profit.")
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(StateFilter(MonthlyCompanyDataForm.kpn))
async def handle_kpn_input(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
):
    kb = await get_company_exists_buttons()

    try:
        kpn = int(message.text)

        is_valid, content = company_information_field_positive_validation(kpn, "kpn")
        if not is_valid:
            await message.answer(content)
            return

        await state.update_data(kpn=kpn)
        data = await state.get_data()

        logging.info(f"Data for company: {data}")
        instance = await create_or_update_monthly_company_information_instance(
            data, user.company, session
        )
        await message.answer(
            f"Monthly data for {str(instance.month).upper()} {instance.year} has been added.",
            reply_markup=kb,
        )
        await state.clear()
    except ValueError:
        await message.answer("Please enter a valid integer for KPN.")
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(StateFilter(ViewMonthlyCompanyDataForm.year))
async def handle_year_selection(message: types.Message, state: FSMContext):
    selected_year = int(message.text)
    await state.update_data(year=selected_year)

    attributes_keyboard = get_monthly_company_information_attributes_keyboard()
    await message.answer(
        "Please select the field you want to view:", reply_markup=attributes_keyboard
    )
    await state.set_state(ViewMonthlyCompanyDataForm.field)


@router.message(StateFilter(ViewMonthlyCompanyDataForm.field))
async def handle_attribute_name_selection(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
):
    logging.info("In {handle_field_selection} function.")
    try:

        data = await state.get_data()
        selected_year = int(data["year"])
        selected_field = message.text.lower()

        records = await get_data_for_the_selected_year_and_attribute(
            user.company.id, selected_field, selected_year, session
        )
        if not records:
            await message.answer("No data available for the selected field.")
            return

        image_stream = generate_monthly_data_chart_based_on_company_records(
            records, selected_field, selected_year
        )

        image_file = BufferedInputFile(image_stream.getvalue(), filename="diagram.png")
        await message.answer_photo(image_file)
    except Exception as exception:
        logging.error(f"Error while sending diagram: {str(exception)}")
        await message.answer(
            f"There was an error generating or sending the diagram."
            f"Exception: {str(exception)}"
        )


@router.message(StateFilter(RetrieveCompanyDataForm.name))
async def handle_name_selection_for_retrieve_company(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    name = message.text
    instance = await get_or_none_company_by_name(name, session)
    await state.update_data(company_id=instance.id)

    years = await get_all_distinct_years_for_the_user_company_by_id(
        instance.id, session
    )
    years_keyboard = generate_list_of_buttons_based_on_list(years)
    await message.answer("Please select a year:", reply_markup=years_keyboard)
    await state.set_state(RetrieveCompanyDataForm.year)


@router.message(StateFilter(RetrieveCompanyDataForm.year))
async def handle_year_selection_for_retrieve_company(
    message: types.Message, state: FSMContext
):
    selected_year = int(message.text)
    await state.update_data(year=selected_year)

    attributes_keyboard = get_monthly_company_information_attributes_keyboard()
    await message.answer(
        "Please select the field you want to view:", reply_markup=attributes_keyboard
    )
    await state.set_state(RetrieveCompanyDataForm.field)


@router.message(StateFilter(RetrieveCompanyDataForm.field))
async def handle_attribute_name_selection_for_retrieve_company(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    logging.info("In {handle_field_selection} function.")

    try:
        data = await state.get_data()
        selected_year = int(data.get("year"))
        selected_company_id = int(data.get("company_id"))
        selected_field = message.text.lower()

        logging.info("Step 2")
        records = await get_data_for_the_selected_year_and_attribute(
            selected_company_id, selected_field, selected_year, session
        )

        image_stream = generate_monthly_data_chart_based_on_company_records(
            records, selected_field, selected_year
        )

        image_file = BufferedInputFile(image_stream.getvalue(), filename="diagram.png")
        await message.answer_photo(image_file)
    except Exception as exception:
        logging.error(f"Error while sending diagram: {str(exception)}")
        await message.answer(
            f"There was an error generating or sending the diagram."
            f"Exception: {str(exception)}"
        )
