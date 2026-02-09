import logging
import json

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from messages.messages_store import get_random_from_prefix, store as messages_store

from Tree.ClassTree import tree

from utility.checkers import file_size_in_limit
from utility.logging_actions import log_action_with_username, log_sending
from utility.tg_utility import (
    change_state_from_button_to_file, change_state_to_tags, language_check,
    set_file_type,
    start_send_fonts_for_query,
    can_go_left as check_left,
    can_go_back as check_back,
    update_data as update_user_info,
    update_indx as update_user_indx,
    get_list_of_files as get_list_of_files,
    download_with_link_query,
    can_go_right as check_right,
    send_file_from_local_for_query, error_final, error_text,
    try_to_delete_message
)

from ...keyboards.buttons import (
    choose_text_inner,
    choose_text_root,
    choose_category_callback,
    get_fonts_buttons_with_feedback,
    go_back_to_main_menu,
    go_back_to_main_menu_with_feedback,
    go_back_to_main_menu_with_feedback_and_freshness,
    ideas_final_buttons_with_feedback,
    tags_buttons
)
from ...keyboards import get_fonts_buttons, how_to_install_fonts_buttons

from Tree.ClassTree import Tree

from YandexDisk import get_download_link, get_file_size
from YandexDisk.YaDiskInfo import TemplateInfo

from DBHandler import (
    get_slides_by_tags_and_template_id,
    get_templates_by_index
)

from pptxHandler import get_template_of_slides, SlideInfo, remove_template

router = Router()
logger = logging.getLogger(__name__)


class WalkerState(StatesGroup):
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()
    tags_search = State()


async def load_config():
    with open("./CONFIG/config.json", "r") as file:
        return json.load(file)


def get_disk_folder_name(query_type, lang: str) -> str:
    """
        Получает название папки на Я. Диске, 
        в которой содержатся материалы соответствующие типу запроса
    """
    if lang == "ru":
        if query_type in ['pres_templates', 'fonts']:
            return 'Шаблоны'
        if query_type == 'search_by_tags':
            return 'Advanced'
        if query_type == 'about_company':
            return 'Слайды о компании'
        if query_type == 'extra_assets':
            return 'Дополнительные материалы'
    else:
        if query_type in ['pres_templates', 'fonts']:
            return 'Templates'
        if query_type == 'search_by_tags':
            return 'Advanced'
        if query_type == 'about_company':
            return 'About company'
        if query_type == 'extra_assets':
            return 'Useful assets'


@router.callback_query(F.data == "pres_templates")
@router.callback_query(F.data == "fonts")
@router.callback_query(F.data == "search_by_tags")
@router.callback_query(F.data == "about_company")
@router.callback_query(F.data == "extra_assets")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
        Обработка основных кнопок в главном меню, инициация обхода дерева Диска
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    # грузим базу
    path_str = tree.root.path
    config = await load_config()
    dist_indx = config['dist']

    # минимально обновляем состояние
    await state.clear()
    await state.set_state(WalkerState.choose_button)
    type_file = await set_file_type(callback_query.data, state)

    # получаем язык пользователя или спрашиваем, если он ещё не выбирал
    lang = await language_check(callback_query)
    if not lang:
        return
    # теперь будем работать с файлами, соотв. языку — обозначаем в путях
    path_str += "/" + lang
    path = [callback_query.data]
    path.append(lang)

    child_list = tree.get_children_names(path_str)
    requested_folder = get_disk_folder_name(callback_query.data, lang)
    requested_tree_node = tree.get_node(path_str+"/"+requested_folder)
    if not requested_tree_node:
        return
    path_str = requested_tree_node.path
    path.append(requested_tree_node.name)
    child_list = tree.get_children_names(path_str)

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)


    await state.update_data(file_name_list=[])
    await update_user_info(state, path, 0, indx_list_end, False, child_list, path_str)

    reply_markup = await choose_category_callback(
        child_list[indx_list_start:indx_list_end],
        can_go_left,
        can_go_right,
        False,
        type_file,
        lang
    )
    text = await choose_text_root(type_file, lang)
    # Костыль, тк в англ версии файл только один
    if (type_file == 'about_company') and (lang == "en"):
        await finish_template_search(callback_query, state)
        return

    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def paginate_template_find(callback_query: CallbackQuery, state: FSMContext, direction, lang: str):
    """
        Обработка переключения между экранами на одном уровне в дереве папок
    """
    config = await load_config()
    dist_indx = config['dist']

    user_info = await state.get_data()
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    can_go_back = user_info['can_go_back']
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    path = user_info['path']

    if direction == "next":
        indx_list_start = indx_list_end
        indx_list_end += dist_indx
    elif direction == "prev":
        indx_list_start -= dist_indx
        indx_list_end -= dist_indx

    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)

    reply_markup = await choose_category_callback(
        child_list[indx_list_start:indx_list_end],
        can_go_left,
        can_go_right,
        can_go_back,
        type_file,
        lang
    )
    text = await choose_text_inner(path[-1], lang)

    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

    await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_button, F.data == "next")
async def next_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes 'next block of directories' action
    """
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)
    
    lang = await language_check(callback_query)
    if not lang:
        return
    
    await paginate_template_find(callback_query, state, "next", lang)


@router.callback_query(WalkerState.choose_button, F.data == "prev")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes 'prev block of directories' action
    """
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)
    
    lang = await language_check(callback_query)
    if not lang:
        return
    
    await paginate_template_find(callback_query, state, "prev", lang)


@router.callback_query(WalkerState.choose_button, F.data == "prev_dir")
async def prev_dir_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes 'prev directory' action
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return
    
    config = await load_config()
    dist_indx = config['dist']

    user_info = await state.get_data()
    path = user_info['path']
    path_str = user_info['path_str']
    type_file = user_info['type_file']

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx

    parent = tree.get_parent(path_str)
    child_list = tree.get_children_names(parent.path)

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)

    reply_markup = await choose_category_callback(
        child_list[indx_list_start:indx_list_end],
        can_go_left,
        can_go_right,
        can_go_back,
        type_file,
        lang
    )

    if parent.name == "root":
        logger.info('Trying get the root folders')
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    elif (parent.name == 'Шаблоны') or (parent.name == 'Templates'):
        text = await choose_text_root(type_file, lang)
    else:
        text = await choose_text_inner(parent.name, lang)

    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list, parent.path)


@router.callback_query(WalkerState.tags_search, F.data == "ideas_from_start")
async def start_tags_search_from_start(callback_query: CallbackQuery, state: FSMContext):
    """
        Обработка выбора идей (тега) со старта, с уже выбраным шаблоном
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return
    
    reply_text = messages_store.get("menu.start_tags_search", lang)
    try:
        if lang == "ru":
            with open("./CONFIG/tags_tree.json", "r") as tags_file:
                tags = json.load(tags_file)
        else:
            with open("./CONFIG/tags_tree_en.json", "r") as tags_file:
                tags = json.load(tags_file)
    except Exception as e:
        logger.info('Error while reading tags_tree')
        logger.info(e)
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    await state.update_data(tags=tags)

    reply_markup = await tags_buttons(tags['sub_categories'], False, True, lang)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def start_tags_search(callback_query: CallbackQuery, state: FSMContext, files_list):
    """
        Переход на корневой экран поиска идей (тега) 
    """

    lang = await language_check(callback_query)
    if not lang:
        return

    file_name = files_list[0][2]
    file_path = files_list[0][1]
    template = file_name[:-5]
    reply_text = messages_store.get("menu.tags_search_on_template", lang, template=template)
    try:
        if lang == "ru":
            with open("./CONFIG/tags_tree.json", "r") as tags_file:
                tags = json.load(tags_file)
        else:
            with open("./CONFIG/tags_tree_en.json", "r") as tags_file:
                tags = json.load(tags_file)
    except Exception as e:
        logger.info('Error while reading tags_tree.json')
        logger.info(e)
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    await change_state_to_tags(state, WalkerState.tags_search, files_list, [file_name], [file_path], tags)

    reply_markup = await tags_buttons(tags['sub_categories'], False, True, lang)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def finish_tags_search(callback_query: CallbackQuery, state: FSMContext, tag, tag_name: str):
    """
        Обработка финального этапа поиска идей для вдохновения: сборка и отправка файла
    """

    lang = await language_check(callback_query)
    if not lang:
        return

    # данные по шаблону
    files_list = await get_list_of_files(state)
    if not files_list:
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    template = files_list[0]
    template_id = template[0]
    template_path = template[1]
    template_name = template[2]

    # получаем слайды по тегам
    slides_list = get_slides_by_tags_and_template_id([tag], template_id)
    if not len(slides_list):
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    try:
        await callback_query.message.edit_text(
            text=messages_store.get("sending.tags_in_process", lang)
        )
    except Exception as e:
        logger.info(e)
    
    # создаём SlideInfo со всеми слайдами выборки и фиксируем шаблон — для ф-ции нарезания
    slide_info = SlideInfo(slides_list[0][0], tag)
    slide_info.add_indexes([s[0] for s in slides_list[1:]])
    template_info = TemplateInfo(template_name, template_path)
    slide_info.add_template_info(template_info)
    
    path_to_save = f'./Data/slides/{callback_query.message.from_user.id}.pptx'
    get_template_of_slides(path_to_save, slide_info)
    try:
        file_name_to_send = f'{tag_name} ({template_name[:-5]}).pptx';
        log_sending(logger, file_name_to_send)
        await send_file_from_local_for_query(callback_query, path_to_save, file_name_to_send)
    except Exception as e:
        logger.info('Error while send_file_from_local_for_query in finish_tags_search')
        logger.info(e)
        reply_markup = await go_back_to_main_menu(lang)
        await try_to_delete_message(callback_query)
        text = await error_text(lang)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=text,
            reply_markup=reply_markup
        )
        return

    reply_markup = await ideas_final_buttons_with_feedback(lang)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=messages_store.get("sending.tags_done", lang),
        reply_markup=reply_markup
    )
    remove_template(path_to_save)


@router.callback_query(WalkerState.tags_search, F.data.isnumeric())
async def tags_search(callback_query: CallbackQuery, state: FSMContext):
    """
        Обработка хождения по дереву тегов
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return
    
    state_info = await state.get_data()
    tags_on_prev_step_dict = state_info['tags']
    chosen_tag_id = int(callback_query.data) - 1

    # if wanna go back
    if (chosen_tag_id == -1):
        cur_tag = tags_on_prev_step_dict['parent']
    else:
        cur_tag = tags_on_prev_step_dict['sub_categories'][chosen_tag_id]
        cur_tag['parent'] = tags_on_prev_step_dict
    await state.update_data(tags=cur_tag)

    if 'sub_categories' in cur_tag:
        # не дошли до листа => ищем тег дальше
        new_tags = cur_tag['sub_categories']
        reply_markup = await tags_buttons(new_tags, ('parent' in cur_tag), True, lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=cur_tag['comment'],
            reply_markup=reply_markup
        )
    else:
        # дошли до листа => запускаем генерацию pptx
        if 'tag' in cur_tag:
            await finish_tags_search(callback_query, state, cur_tag['tag'], cur_tag['name'])
        else:
            # такого вообще не должно быть
            logger.info('ATTENTION: Error in tags_search while getting tag')
            text = await error_text(lang)
            await error_final(callback_query, text, lang)


async def finish_template_search(callback_query: CallbackQuery, state: FSMContext):
    """
        Сбор и отправка файла
    """

    lang = await language_check(callback_query)
    if not lang:
        return

    user_info = await state.get_data()

    path = user_info['path']
    path_str = user_info['path_str']
    parent_name = path[-1]

    files_list = await get_list_of_files(state)
    type_file = user_info['type_file']
    if not files_list:
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    file_name = files_list[0][2]
    file_path = files_list[0][1]
    await change_state_from_button_to_file(state, files_list, [file_name], WalkerState.choose_file, [file_path])
    await state.update_data(file_id=files_list[0][0])

    try:
        link = get_download_link(str(file_path) + '/' + str(file_name))
        file_size = get_file_size(str(file_path) + '/' + str(file_name))
    except Exception:
        reply_markup = await go_back_to_main_menu(lang)
        await try_to_delete_message(callback_query)
        text = await error_text(lang)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=text,
            reply_markup=reply_markup
        )
        return

    if file_size_in_limit(file_size):
        await callback_query.message.edit_text(
            text=get_random_from_prefix("waiting", lang)
        )
        try:
            log_sending(logger, str(file_path) + '/' + str(file_name))
            # log_sending(logger, path_str)
            await download_with_link_query(callback_query, link, file_name, lang)
            if type_file == "extra_assets":
                if ("Логотипы" in parent_name) or ("logos" in parent_name):
                    reply_markup = await go_back_to_main_menu_with_feedback_and_freshness(lang)
                else:
                    reply_markup = await go_back_to_main_menu_with_feedback(lang)
                await try_to_delete_message(callback_query)
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=messages_store.get("sending.extra_assets_done", lang),
                    reply_markup=reply_markup
                )
            else:
                reply_markup = await get_fonts_buttons_with_feedback(lang)
                await try_to_delete_message(callback_query)
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=messages_store.get("sending.templates_done", lang),
                    reply_markup=reply_markup
                )
        except Exception as e:
            text = await error_text(lang)
            await error_final(callback_query, text, lang)
            logger.info(e)
            return
    else:
        reply_markup = await get_fonts_buttons(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Забирай шаблон по <a href='{link}'>ссылке</a>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )


@router.callback_query(WalkerState.choose_button, F.data == "get_fonts_from_all_pres")
async def get_fonts_from_all_pres(callback_query: CallbackQuery, state: FSMContext):
    """
        Обработка конпки "скачать сразу все шрифты"
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    user_info = await state.get_data()
    path = '/'.join(user_info['path'][1:])
    
    # определяем сообщение и имя архива — отдельно обрабатываем корень
    item_name = ''
    try:
        if (user_info['path'][-1] == 'Шаблоны') or (user_info['path'][-1] == 'Templates'):
            item_name = 'all'
            await callback_query.message.edit_text(
                    text=messages_store.get("sending.all_fonts", lang),
                    parse_mode=ParseMode.HTML
                )
        else:
            # отрезаем два символа – эмоджи и пробел
            if lang == 'ru':
                item_name = user_info['path'][-1][2:]
            else:
                item_name = user_info['path'][-1]
            await callback_query.message.edit_text(
                    text=messages_store.get("sending.fonts_for_unit", lang, item_name=item_name),
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        logger.info(e)
    try:
        if lang == 'ru':
            zip_name = f'Шрифты {item_name}'
        else:
            zip_name = f'Fonts {item_name}'
        log_sending(logger, "Fonts " + zip_name)
        await start_send_fonts_for_query(callback_query, path, zip_name, lang)
    except Exception as e:
        logger.info(e)
        return
    try:
        reply_markup = await how_to_install_fonts_buttons(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=get_random_from_prefix("done", lang),
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.info(e)


@router.callback_query(WalkerState.choose_button, F.data.isnumeric())
async def navigate_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Имитация хождения по директориям при поиске материалов
    """

    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return
    
    config = await load_config()

    user_info = await state.get_data()
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    indx_list_start = user_info['indx_list_start']
    path = user_info['path']
    path_str = user_info['path_str']

    indx_child = indx_list_start + int(callback_query.data) - 1
    path.append(child_list[indx_child])
    next_path_str = path_str + "/" + child_list[indx_child]

    child_list = tree.get_children_names(next_path_str)

    indx_list_start = 0
    dist_indx = config['dist']
    indx_list_end = dist_indx + indx_list_start

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list, next_path_str)

    # проверяем, спустились ли до "листа" (нет вложенных директорий)
    # если спустились, отправляемся на обработку материалов для запроса
    if not child_list:
        files_list = await get_list_of_files(state)
        if type_file == 'font':
            await get_fonts_from_all_pres(callback_query, state)
        if type_file == 'template':
            await finish_template_search(callback_query, state)
        if type_file == 'search_by_tags':
            await start_tags_search(callback_query, state, files_list)
        if type_file == 'about_company':
            await finish_template_search(callback_query, state)
        if type_file == 'extra_assets':
            await finish_template_search(callback_query, state)
    else:
        # отдельно рассматривается случай со шрифтами – для них не хотим спускаться до уровня шаблонов — останавливаемся на уровне БЮ (5)
        if type_file == 'font' and len(path) == 6:
            await get_fonts_from_all_pres(callback_query, state)
        else:
            reply_markup = await choose_category_callback(
                child_list[indx_list_start:indx_list_end],
                can_go_left,
                can_go_right,
                can_go_back,
                type_file,
                lang
            )
            text = await choose_text_inner(path[-1], lang)
            await callback_query.message.edit_text(
                text=text, 
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
