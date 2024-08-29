import json

from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import send_document

from DBHandler import (get_templates_from_child_directories,
                                   get_fonts_from_child_directories)
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import CallbackQuery
import io
import aiohttp
from aiogram.enums import ChatAction
from aiogram.utils.chat_action import ChatActionSender
import urllib.request
import os
import shutil
import zipfile

from TelegramHandler.keyboards import go_back_to_main_menu
from YandexDisk import get_download_link


async def can_go_right(indx_list_end: int, len_child_list: int) -> bool:
    return indx_list_end < len_child_list


async def can_go_left(indx_list_start: int) -> bool:
    return indx_list_start != 0


async def can_go_back(user_data) -> bool:
    return not len(user_data) == 1


async def update_data(state: FSMContext, path, indx_list_start, indx_list_end, can_go_back, child_list) -> None:
    await state.update_data(path=path)
    await state.update_data(can_go_back=can_go_back)
    await state.update_data(child_list=child_list)
    await update_indx(state, indx_list_start, indx_list_end)


async def update_indx(state: FSMContext, indx_list_start, indx_list_end) -> None:
    await state.update_data(indx_list_start=indx_list_start)
    await state.update_data(indx_list_end=indx_list_end)


async def get_list_of_files(state: FSMContext) -> list:
    user_info = await state.get_data()
    list_of_path = user_info['path']
    # Check type of search
    if list_of_path[0] == "Шаблон презентаций":
        path = '/'.join(list_of_path[1:])
        list_of_files = await get_templates_from_child_directories(path)
    elif list_of_path[0] == "Корпоративные шрифты":
        path = '/'.join(list_of_path[1:])
        list_of_files = await get_templates_from_child_directories(path)
    # elif list_of_path[0] == "Изображения":
    #     path = '/'.join(list_of_path[1:])
    #     list_of_files = get_images_from_child_directories(path)
    # elif list_of_path[0] == "Готовые слайды о компании":
    #     path = '/'.join(list_of_path[1:])
    #     list_of_files = await get_templates_from_child_directories(path)
    else:
        path = '/'.join(list_of_path[1:])
        list_of_files = await get_templates_from_child_directories(path)
    return list_of_files


async def from_button_to_file(state: FSMContext,
                              files_list: list, file_name_list: list, to_state, paths_list: list) -> None:
    global dist_indx
    user_info = await state.get_data()
    path = user_info['path']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    await state.set_state(to_state)
    await state.update_data(path=path)
    await state.update_data(indx_list_start=indx_list_start)
    await state.update_data(indx_list_end=indx_list_end)
    await state.update_data(child_list=child_list)
    await state.update_data(files_list=files_list)
    await state.update_data(file_name_list=file_name_list)
    await state.update_data(type_file=type_file)
    await state.update_data(paths_list=paths_list)


async def change_state_to_tags(state: FSMContext, to_state,
                              files_list: list, file_name_list: list, paths_list: list, tags: list) -> None:
    global dist_indx
    user_info = await state.get_data()
    path = user_info['path']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    await state.set_state(to_state)
    await state.update_data(path=path)
    await state.update_data(indx_list_start=indx_list_start)
    await state.update_data(indx_list_end=indx_list_end)
    await state.update_data(child_list=child_list)
    await state.update_data(files_list=files_list)
    await state.update_data(file_name_list=file_name_list)
    await state.update_data(type_file=type_file)
    await state.update_data(paths_list=paths_list)
    await state.update_data(tags=tags)


async def admin_from_chose_dir_to_choose_file(state: FSMContext,
                                              files_list: list, file_name_list: list, to_state) -> None:
    global dist_indx
    user_info = await state.get_data()
    path = user_info['path']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    child_list = user_info['child_list']
    await state.set_state(to_state)
    await state.update_data(path=path)
    await state.update_data(indx_list_start=indx_list_start)
    await state.update_data(indx_list_end=indx_list_end)
    await state.update_data(child_list=child_list)
    await state.update_data(files_list=files_list)
    await state.update_data(file_name_list=file_name_list)


async def set_file_type(type_file: str, state: FSMContext) -> str:
    if type_file in ("Шаблон презентаций", "pres_templates"):
        await state.update_data(type_file='template')
        return 'template'
    elif type_file in ("Корпоративные шрифты", "fonts"):
        await state.update_data(type_file='font')
        return 'font'
    # elif type_file in ("Готовые слайды о компании", "slides"):
    #     await state.update_data(type_file='slide')
    #     return 'slide'
    elif type_file == "search_by_tags":
        await state.update_data(type_file='search_by_tags')
        return 'search_by_tags'
    return 'None'


async def send_big_file(message: types.Message, link, file_name):
    file = io.BytesIO()
    url = link
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            result_bytes = await response.read()

    file.write(result_bytes)
    try:
        await message.reply_document(
            document=types.BufferedInputFile(
                file=file.getvalue(),
                filename=f'{file_name}',
            ),
        )
    except TelegramNetworkError:
        await message.answer(
            text='Не удалось загрузить файл, попробуйте позже'
        )
        raise 'TelegramNetworkError'


async def send_big_file_query(callback_query: CallbackQuery, link, file_name):
    file = io.BytesIO()
    url = link
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            result_bytes = await response.read()

    file.write(result_bytes)
    try:
        await send_document.SendDocument(
            chat_id=callback_query.message.chat.id,
            document=types.BufferedInputFile(
                file=file.getvalue(),
                filename=f'{file_name}',
            ),
        ).as_(callback_query.bot)
    except TelegramNetworkError:
        reply_markup = await go_back_to_main_menu()
        await callback_query.message.edit_text(
            text='Не удалось загрузить файл, попробуйте позже',
            reply_markup=reply_markup
        )
        raise 'TelegramNetworkError'


async def download_with_link_query(callback_query: CallbackQuery, link, file_name):
    await callback_query.bot.send_chat_action(
        chat_id=callback_query.message.chat.id,
        action=ChatAction.UPLOAD_DOCUMENT,
    )
    async with ChatActionSender.upload_document(
        bot=callback_query.bot,
        chat_id=callback_query.message.chat.id,
    ):
        await send_big_file_query(callback_query, link, file_name)


async def send_file_from_local_for_query(callback_query: CallbackQuery, path, filename):
    await send_document.SendDocument(
        chat_id=callback_query.message.chat.id,
        document=types.FSInputFile(
            path=path,
            filename=filename
        )
    ).as_(callback_query.bot)


async def send_zips_for_query(callback_query: CallbackQuery, list_data):
    for_zip_path = f'Data/forZip'
    user_zip_path = for_zip_path + '/' + f'{callback_query.from_user.id}'
    archive_name = f'{callback_query.from_user.id}.zip'
    path_to_zip = for_zip_path + '/' + archive_name
    try:
        if not os.path.exists(user_zip_path):
            os.mkdir(user_zip_path)
        counter = 1
        for file in list_data:
            link = get_download_link(file[1] + '/' + file[3])
            try:
                urllib.request.urlretrieve(link, user_zip_path + f'/{counter}_{file[3]}')
                counter += 1
            except Exception as X:
                print('error while reading url')
                print(X)
        merge_fonts(user_zip_path, path_to_zip)
        await send_file_from_local_for_query(callback_query, path_to_zip, 'Fonts.zip')
    except:
        await callback_query.answer(
            text=f'Что-то пошло не так :( Сообщи '
                  f'{json.load(open("./config.json"))["owner"]} или попробуй позже'
        )
    shutil.rmtree(user_zip_path)
    os.remove(path_to_zip)


# TODO ???
# Enter the reply message, the path on Yadisk, and the local path
# to download the files so that the bot sends the user the
# correct files
async def start_send_fonts_for_query(callback_query: CallbackQuery, YDpath):
    list_fonts = get_fonts_from_child_directories(YDpath)
    if len(list_fonts) == 0:
        print('expected fonts dont found')
        reply_markup = await go_back_to_main_menu()
        await callback_query.message.edit_text(
            text='По данному запросу не найдено ни одного шрифта!',
            reply_markup=reply_markup
        )
    try:
        await callback_query.bot.send_chat_action(
            chat_id=callback_query.message.chat.id,
            action=ChatAction.UPLOAD_DOCUMENT,
        )

    except:
        # TODO обработать ошибки
        print('Error')
    try:
        async with ChatActionSender.upload_document(
            bot=callback_query.bot,
            chat_id=callback_query.message.chat.id,
        ):
            await send_zips_for_query(callback_query, list_fonts)
    except:
        # TODO обработать ошибки
        print('Error')


def merge_fonts(input_folder, output_zip):
    # Set for unique fonts
    unique_files = set()

    with zipfile.ZipFile(output_zip, 'w') as output_zip_file:
        dir_name = 'Fonts'
        # output_zip_file.mkdir(dir_name)
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        for font_file in zip_ref.namelist():
                            if font_file.endswith(('.otf', '.ttf')):
                                if font_file not in unique_files:
                                    unique_files.add(font_file)
                                    try:
                                        print(font_file)
                                        file_data = zip_ref.read(font_file)
                                        output_zip_file.writestr(
                                            os.path.join(
                                                dir_name,
                                                os.path.basename(font_file)
                                            ),
                                            file_data,
                                            compress_type=zipfile.ZIP_DEFLATED,
                                        )
                                    except:
                                        print('Cant add font to zip')
