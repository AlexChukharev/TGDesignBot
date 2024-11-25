from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile

from telegram import InputFile
from telegram.constants import ParseMode

from utility.checkers import is_user

from ..keyboards.start_and_simple_button import main_menu_buttons_from_query


router = Router()

users = [928962436, 58566456, 170108064]


class UserStates(StatesGroup):
    in_main_menu = State()
    in_choose_category = State()
    find_images = State()
    find_templates = State()
    find_slides_about_company = State()
    find_fonts = State()
    find_ready_structs = State()


@router.message(Command("start"), lambda message: is_user(message.from_user.id))
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await message.answer(
        text=f'Привет, {message.from_user.first_name}!\nЯ – бот-помощник команды визуальных коммуникаций. '\
        f'Могу найти материалы для презентаций, подобрать подходящую визуализацию или помочь поставить задачу команде дизайнеров\n\n'\
        f'Я только начинаю свой путь и стремлюсь развиваться, поэтому буду рад твоей обратной связи и идеям для улучшения!',
        parse_mode=ParseMode.HTML
    )
    await message.answer_photo(
        FSInputFile(path="test3.png")
    )
    await message.answer(
        text="Ищешь что-то?",
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "main_menu", lambda message: is_user(message.from_user.id))
async def main_start_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await callback_query.message.edit_text(
        f'Ищешь что-то?',
        reply_markup=reply_markup
    )


@router.message(Command(commands=["menu"]), lambda message: is_user(message.from_user.id))
@router.message(F.text.lower() == "в главное меню")
async def cmd_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query()
    await message.answer(
        text="Ищешь что-то?",
        reply_markup=reply_markup
    )
