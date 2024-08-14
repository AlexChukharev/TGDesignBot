import json
import random
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utility.checkers import is_admin_with_json
from ...keyboards import to_admin_menu
from ...keyboards.start_and_simple_button import only_main_menu_button_kb, go_to_main_menu

router = Router()


class AdminState(StatesGroup):
    accept_add = State()
    input_id = State()


@router.callback_query(F.data == "new_admin_add",
                       lambda callback_query: is_admin_with_json(callback_query.from_user.id))
async def initiate_admin_add(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AdminState.input_id)
    await callback_query.message.edit_text(text="Введите id нового администратора:",
                                           reply_markup=to_admin_menu())


@router.message(AdminState.input_id)
async def process_new_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(text='Нужно ввести числовое значение. Попробуйте снова')
        return

    await state.clear()
    with open("./admins.json", "r") as file:
        config = json.load(file)

    new_admin_id = int(message.text)
    if new_admin_id in config["admin_id"]:
        await message.answer(text='Данный пользователь уже является администратором!',
                             reply_markup=only_main_menu_button_kb())
        return

    await state.set_state(AdminState.accept_add)
    await state.update_data(new_admin_id=message.text)
    await message.delete()

    key = random.randint(100, 999)
    await state.update_data(key=str(key))

    confirmation_text = f"Подтвердите добавление {message.text} отправив '{key}'"
    await message.answer(text=confirmation_text, reply_markup=await go_to_main_menu())


@router.message(AdminState.accept_add)
async def confirm_new_admin(message: Message, state: FSMContext):
    user_info = await state.get_data()
    key = user_info['key']
    new_admin_id = int(user_info['new_admin_id'])

    if message.text != key:
        await message.answer(text='Введён неправильный код или команда', reply_markup=await go_to_main_menu())
        return

    await state.clear()
    with open("./admins.json", "r") as file:
        config = json.load(file)

    config["admin_id"].append(new_admin_id)

    with open("./admins.json", "w") as file:
        json.dump(config, file)

    await message.answer(text=f'Пользователь {new_admin_id} успешно добавлен!', reply_markup=only_main_menu_button_kb())
