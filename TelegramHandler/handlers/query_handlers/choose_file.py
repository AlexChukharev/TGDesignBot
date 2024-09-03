import json
from telegram.constants import ParseMode

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from utility.tg_utility import error_final, can_go_right as check_right, \
    download_with_link_query, send_file_from_local_for_query, error_text
from utility.tg_utility import can_go_left as check_left
from utility.tg_utility import update_indx as update_user_indx

from DBHandler import (
    get_fonts_by_template_id,
    delete_template,
    get_template_id_by_name
)

from YandexDisk.YaDiskInfo import TemplateInfo
from YandexDisk import get_download_link, get_file_size

from ...keyboards import go_back_to_main_menu, how_to_install_fonts_buttons, get_fonts_buttons

router = Router()


class WalkerState(StatesGroup):
    # TODO не только это — изучить и добавить описание
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()


# @router.callback_query(WalkerState.choose_file, F.data == "next")
# async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
#     with open("./config.json", "r") as file:
#         config = json.load(file)
#         dist_indx = config['dist']
#
#         user_info = await state.get_data()
#         indx_list_end = user_info['indx_list_end']
#         file_name_list = user_info['file_name_list']
#         paths_list = user_info['paths_list']
#
#         indx_list_start = indx_list_end
#         indx_list_end = indx_list_end + dist_indx
#
#         can_go_right = await check_right(indx_list_end, len(file_name_list))
#         can_go_left = await check_left(indx_list_start)
#
#         reply_markup = await choose_file_kb_query(file_name_list[indx_list_start:indx_list_end], can_go_left,
#                                                   can_go_right)
#         text = await choose_one_file(
#             file_name_list[indx_list_start:indx_list_end],
#             paths_list[indx_list_start:indx_list_end]
#         )
#
#         await callback_query.message.edit_text(
#             text=text,
#             reply_markup=reply_markup
#         )
#
#         await update_user_indx(state, indx_list_start, indx_list_end)


# @router.callback_query(WalkerState.choose_file, F.data == "prev")
# async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
#     with open("./config.json", "r") as file:
#         config = json.load(file)
#         dist_indx = config['dist']
#
#         user_info = await state.get_data()
#         indx_list_start = user_info['indx_list_start']
#         indx_list_end = user_info['indx_list_end']
#         file_name_list = user_info['file_name_list']
#         paths_list = user_info['paths_list']
#
#         indx_list_start -= dist_indx
#         indx_list_end -= dist_indx
#
#         can_go_right = await check_right(indx_list_end, len(file_name_list))
#         can_go_left = await check_left(indx_list_start)
#
#         reply_markup = await choose_file_kb_query(file_name_list[indx_list_start:indx_list_end], can_go_left,
#                                                   can_go_right)
#         text = await choose_one_file(
#             file_name_list[indx_list_start:indx_list_end],
#             paths_list[indx_list_start:indx_list_end]
#         )
#
#         await callback_query.message.edit_text(
#             text=text,
#             reply_markup=reply_markup
#         )
#         await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_file, F.data == "get_fonts")
async def get_fonts(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    template_id = user_info["file_id"]
    list_fonts = get_fonts_by_template_id(template_id)

    if len(list_fonts) == 0:
        text = await error_text()
        await error_final(callback_query, text)
        return

    try:
        await callback_query.message.edit_text(
            text="Отправляю..."
        )
    except:
        print('Error')
    try:
        path = list_fonts[0][1] + '/' + list_fonts[0][3]
        link = get_download_link(path)
        await download_with_link_query(callback_query, link, 'fonts.zip')
        reply_markup = await how_to_install_fonts_buttons()
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Готово!",
            reply_markup=reply_markup
        )
    except:
        pass


@router.callback_query(WalkerState.choose_file, F.data == "install_fonts_help")
async def send_info(callback_query: CallbackQuery):
    try:
        await callback_query.message.edit_text(
            text='Готовлю инструкцию, секунду'
        )
    except:
        print('Proxy error')
    path = './Data/Appdata/00 How to install fonts.pdf'
    await send_file_from_local_for_query(callback_query, path, 'How to install fonts.pdf')
    reply_markup = await go_back_to_main_menu()
    await callback_query.message.delete()
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Это тебе поможет!',
        reply_markup=reply_markup
    )


# Обрабатывает поиск материалов по Яндекс Диску
# TODO описание функции
@router.callback_query(WalkerState.choose_file)
async def choose_category(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_index = config['dist']
        user_info = await state.get_data()
        type_file = user_info['type_file']
        indx_list_start = user_info['indx_list_start']
        indx_child = indx_list_start + int(callback_query.data) - 1
        file_name_list = user_info['file_name_list']
        file_name_from_list = file_name_list[indx_child]

        file_id = None
        link = None
        file_name = None
        file_path = None
        files_list = user_info['files_list']

        for file in files_list:
            if file[2] == file_name_from_list:
                file_id = file[0]
                file_path = file[1]
                file_name = file[2]

                await state.update_data(file_id=file_id)
                await state.update_data(link=link)
                await state.update_data(file_path=file_path)
                await state.update_data(file_name=file_name)
                break

        if type_file == 'template':

            try:
                link = get_download_link(str(file_path) + '/' + str(file_name))
                file_size = get_file_size(str(file_path) + '/' + str(file_name))
            except Exception:
                # await callback_query.message.edit_text(
                #     text="Не удалось найти данный файл, возможно он был перемещён или удалён."
                # )
                text = await error_text()
                await error_final(callback_query, text)
                template_info = TemplateInfo(str(file_name), str(file_path))
                template_id = get_template_id_by_name(template_info.path, template_info.name)
                delete_template(template_id)
                return

            # TODO перенести проверку в отдельную функцию и проверить, где еще она нужна
            if file_size < 50*1024*1024:
                await callback_query.message.edit_text(
                    text=" Супер, отправляю! Это займет минутку"
                )
                try:
                    await download_with_link_query(callback_query, link, file_name)
                    reply_markup = await get_fonts_buttons()
                    await callback_query.message.delete()
                    await callback_query.bot.send_message(
                        chat_id=callback_query.from_user.id,
                        text="Держи файл! И не забудь проверить, что у тебя есть корпоративные шрифты)",
                        reply_markup=reply_markup
                    )

                except:
                    text = await error_text()
                    await error_final(callback_query, text)
                    return
            else:
                reply_markup = await get_fonts_buttons()
                await callback_query.message.delete()
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=f"Забирай шаблон по <a href='{link}'>ссылке</a>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )

        if type_file == 'search_by_tags':
            reply_markup = await go_back_to_main_menu()
            await callback_query.message.edit_text(
                text="Попался :(",
                reply_markup=reply_markup
            )
            pass

        if type_file == 'font':
            font_name = get_fonts_by_template_id(file_id)
            if len(font_name) == 0:
                text = await error_text()
                await error_final(callback_query, text)
                return
            try:
                link = get_download_link(file_path + '/' + font_name[0][3])
            except Exception:
                text = await error_text()
                await error_final(callback_query, text)
                return
            try:
                await callback_query.message.edit_text(
                    text="Отправляю, секунду..."
                )
            except:
                print('Error')
            try:
                await download_with_link_query(callback_query, link, 'fonts.zip')
                reply_markup = await get_fonts_buttons()
                await callback_query.message.delete()
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="Готово!",
                    reply_markup=reply_markup
                )
            except:
                print('Font send error')
