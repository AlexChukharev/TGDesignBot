from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from ..keyboards.start_and_simple_button import main_menu_buttons_from_query

router = Router()

users = [928962436, 58566456, 197284014]


class UserStates(StatesGroup):
    in_main_menu = State()
    in_choose_category = State()
    find_images = State()
    find_templates = State()
    find_slides_about_company = State()
    find_fonts = State()
    find_ready_structs = State()


@router.message(Command("start"), lambda message: message.from_user.id in users)
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await message.answer(
        f'Привет, {message.from_user.first_name}! Я ViscommsBot, чем могу помочь?',
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "start", lambda message: message.from_user.id in users)
async def main_start_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await callback_query.message.edit_text(
        f'Чем могу помочь?',
        reply_markup=reply_markup
    )


@router.message(Command(commands=["menu"]), lambda message: message.from_user.id in users)
@router.message(F.text.lower() == "в главное меню")
async def cmd_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await message.answer(
        text="Чем могу помочь?",
        reply_markup=reply_markup
    )
