import json
from random import randint

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from utility.tg_utility import can_go_right as check_right, can_go_left as check_left, \
    update_indx as update_user_indx
from ...keyboards import choose_tags_query
from ...keyboards.choose_file_keyboard import choose_file_for_delete, back_in_last_state
from YandexDisk.YaDiskHandler import delete_from_disk

router = Router()


class AdminState(StatesGroup):
    choose_button = State()
    choose_category = State()
    choose_file = State()


async def update_file_list(callback_query: CallbackQuery, state: FSMContext, indx_list_start: int, indx_list_end: int):
    with open("./config.json", "r") as file:
        dist_indx = json.load(file)['dist']
        user_info = await state.get_data()
        file_name_list = user_info['file_name_list']

        can_go_right = await check_right(indx_list_end, len(file_name_list))
        can_go_left = await check_left(indx_list_start)

        reply_markup = await choose_file_for_delete(file_name_list[indx_list_start:indx_list_end], can_go_left,
                                                  can_go_right)
        text = await choose_tags_query(file_name_list[indx_list_start:indx_list_end])

        await callback_query.message.edit_text(text="Выберите один из файлов\n\n" + text, reply_markup=reply_markup)
        await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(AdminState.choose_file, F.data == "next")
async def go_to_next_page(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    indx_list_end = user_info['indx_list_end']
    indx_list_start = indx_list_end
    indx_list_end += json.load(open("config.json", "r"))['dist']

    await update_file_list(callback_query, state, indx_list_start, indx_list_end)


@router.callback_query(AdminState.choose_file, F.data == "prev")
async def go_to_prev_page(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    dist_indx = json.load(open("config.json", "r"))['dist']

    indx_list_start -= dist_indx
    indx_list_end -= dist_indx

    await update_file_list(callback_query, state, indx_list_start, indx_list_end)


@router.callback_query(AdminState.choose_file, F.data == 'back_in_state_last')
async def go_back_in_state(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']

    await update_file_list(callback_query, state, indx_list_start, indx_list_end)


@router.callback_query(AdminState.choose_file)
async def confirm_delete_file(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    key = randint(100, 999)
    indx_list_start = user_info['indx_list_start']
    file_name_list = user_info['file_name_list']
    indx_delete_file = indx_list_start + int(callback_query.data) - 1

    await state.update_data(key=str(key))
    await state.update_data(file_for_delete=file_name_list[indx_delete_file])

    reply_markup = back_in_last_state()
    await callback_query.message.edit_text(
        text=f"Подтвердите удаление кодом {key} в чат, или отмените действие",
        reply_markup=reply_markup
    )


@router.message(AdminState.choose_file)
async def delete_file(message: Message, state: FSMContext):
    user_info = await state.get_data()
    key = user_info['key']
    file_for_delete = user_info['file_for_delete']

    if message.text != key:
        await message.answer(text='Введен неправильный код или команда')
        return

    await message.answer(text='Данный файл удаляется...')

    files_list = user_info['files_list']
    file_path, file_name = None, None

    for file in files_list:
        if file[2] == file_for_delete:
            file_path, file_name = file[1], file[2]
            await state.update_data(file_id=file[0], file_path=file_path, file_name=file_name)
            break

    if file_path and file_name:
        try:
            delete_from_disk(f"{file_path}/{file_name}")
        except Exception as e:
            await message.answer(text=f'Ошибка при удалении файла: {str(e)}')
            return

        await message.answer(text='Данный файл успешно удален!')
    else:
        await message.answer(text='Файл не найден для удаления.')

    await state.clear()
