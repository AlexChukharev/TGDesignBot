from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from ..keyboards.start_and_simple_button import start_menu_kb, start_menu_kb_query, main_menu_buttons_from_query
from ..keyboards.InlineKeyboards.searchKB import build_choose_kb

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
    reply_markup = await main_menu_buttons_from_query(message)
    await message.answer(
        f'Привет, {message.from_user.first_name}! Я ViscommsBot, чем могу помочь?',
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "start", lambda message: message.from_user.id in users)
async def main_start_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query(callback_query)
    await callback_query.message.edit_text(
        f'Чем могу помочь?',
        reply_markup=reply_markup
    )


@router.message(Command(commands=["menu"]), lambda message: message.from_user.id in users)
@router.message(F.text.lower() == "в главное меню")
async def cmd_cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    reply_markup = await main_menu_buttons_from_query(message)
    await message.answer(
        text="Чем могу помочь?",
        reply_markup=reply_markup
    )


@router.callback_query(F.data == 'main_menu')
async def cmd_cancel_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text="Чем могу помочь?",
        reply_markup=start_menu_kb_query(callback_query)
    )


# @router.message(StateFilter(None), Command(commands=["choose_category"]), lambda message: message.from_user.id in users)
# @router.message(F.text.lower() == "поиск материалов")
# @router.message(Command("cat", prefix="!/"))
# async def choose_category_handler(message: Message, state: FSMContext):
#     reply_markup = await build_choose_kb()
#     await message.answer(
#         text="Что вас интересует?",
#         reply_markup=reply_markup
#     )
#     await state.set_state(UserStates.in_choose_category)
#
#
# @router.message(StateFilter(None), Command(commands=["choose_category"]), lambda message: message.from_user.id in users)
# @router.message(Command("cat", prefix="!/"))
# @router.callback_query(F.data == "menu_choose")
# async def choose_category_handler(callback_query: CallbackQuery, state: FSMContext):
#     reply_markup = await build_choose_kb()
#     await callback_query.message.edit_text(
#         text="Что вас интересует?",
#         reply_markup=reply_markup
#     )
#     await state.set_state(UserStates.in_choose_category)
#
#
# @router.callback_query(F.data == "menu_choose")
# async def choose_category_handler(callback_query: CallbackQuery, state: FSMContext):
#     reply_markup = await build_choose_kb()
#     await callback_query.message.edit_text(
#         text="Что вас интересует?",
#         reply_markup=reply_markup
#     )
#     await state.set_state(UserStates.in_choose_category)
