import logging 
import json

from aiogram.enums import ParseMode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from utility.tg_utility import error_final, try_to_delete_message, \
    download_with_link_query, send_file_from_local_for_query, error_text

from DBHandler import (
    get_fonts_by_template_id,
    delete_template,
    get_template_id_by_name
)

from YandexDisk.YaDiskInfo import TemplateInfo
from YandexDisk import get_download_link, get_file_size

from ...keyboards import go_back_to_main_menu, how_to_install_fonts_buttons, get_fonts_buttons


router = Router()
logger = logging.getLogger(__name__)


class WalkerState(StatesGroup):
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()


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
    except Exception as e:
        text = await error_text()
        await error_final(callback_query, text)
        logger.info(e)
        return
    
    try:
        path = list_fonts[0][1] + '/' + list_fonts[0][3]
        link = get_download_link(path)
        await download_with_link_query(callback_query, link, 'fonts.zip')

        reply_markup = await how_to_install_fonts_buttons()
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Готово!",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.info(e)


@router.callback_query(WalkerState.choose_file, F.data == "install_fonts_help")
@router.callback_query(WalkerState.choose_button, F.data == "install_fonts_help")
async def send_info(callback_query: CallbackQuery):
    try:
        await callback_query.message.edit_text(
            text='Готовлю инструкцию, секунду'
        )
    except Exception as e:
        logger.info(e)
    path = './Data/Appdata/Инструкция по установке шрифтов.pdf'
    await send_file_from_local_for_query(callback_query, path, 'Инструкция по установке шрифтов.pdf')
    reply_markup = await go_back_to_main_menu()
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Это тебе поможет!',
        reply_markup=reply_markup
    )


# Обрабатывает поиск материалов по Яндекс Диску
# TODO описание функции
@router.callback_query(WalkerState.choose_file)
async def choose_category(callback_query: CallbackQuery, state: FSMContext):
    with open("./CONFIG/config.json", "r") as file:
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
            full_path = str(file_path) + '/' + str(file_name)
            try:
                link = get_download_link(full_path)
                file_size = get_file_size(full_path)
            except Exception as e:
                text = await error_text()
                await error_final(callback_query, text)
                template_info = TemplateInfo(str(file_name), str(file_path))
                template_id = get_template_id_by_name(template_info.path, template_info.name)
                delete_template(template_id)
                logger.info("Error while getting info for ", str(file_path) + '/' + str(file_name))
                logger.info(e)
                return

            # TODO перенести проверку в отдельную функцию и проверить, где еще она нужна
            if file_size < 50*1024*1024:
                await callback_query.message.edit_text(
                    text=" Супер, отправляю! Это займет минутку"
                )
                try:
                    await download_with_link_query(callback_query, link, file_name)
                    reply_markup = await get_fonts_buttons()
                    await try_to_delete_message(callback_query)
                    await callback_query.bot.send_message(
                        chat_id=callback_query.from_user.id,
                        text="Держи файл! И не забудь установить корпоративные шрифты",
                        reply_markup=reply_markup
                    )

                except Exception as e:
                    text = await error_text()
                    await error_final(callback_query, text)
                    logger.info(e)
                    return
            else:
                reply_markup = await get_fonts_buttons()
                await try_to_delete_message(callback_query)
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
