import logging

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.bot.states.company import CompanyCreationForm
from src.modules.company.validations import (
    company_creation_validations,
    company_exists_validations,
)
from src.modules.company.services import create_company, delete_company


router = Router()


async def get_company_exists_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="View Company"),
                KeyboardButton(text="Add Information"),
            ],
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

        new_company = await create_company(user.id, company_name, session)
        await message.answer(
            f"Company '{new_company.name}' has been created!", reply_markup=kb
        )
        await state.clear()
    except Exception as exception:
        logging.error(exception)
        await message.answer(str(exception))


@router.message(lambda message: message.text == "Delete Company")
async def handle_delete_company(
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
