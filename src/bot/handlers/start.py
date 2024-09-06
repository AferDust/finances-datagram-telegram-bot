import logging

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.models import User
from src.bot.handlers.company import send_company_options


router = Router()


async def get_start_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="My Company"),
                KeyboardButton(text="List of Companies"),
            ]
        ],
        resize_keyboard=True,
    )


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    await message.answer("Welcome! You can do this action.")
    start_button_markup = await get_start_buttons()
    await message.answer("Choose an option:", reply_markup=start_button_markup)


@router.message(lambda message: message.text == "My Company")
async def my_company_command_handler(message: types.Message, user: User):
    logging.info(f"Handling 'My Company' command from user: {user.id}")
    await send_company_options(user, message)


@router.message(lambda message: message.text == "Exit")
async def handle_exit(message: types.Message, state: FSMContext):
    start_button_markup = await get_start_buttons()
    await state.clear()
    await message.answer(
        "You have exited to the main menu.", reply_markup=start_button_markup
    )
