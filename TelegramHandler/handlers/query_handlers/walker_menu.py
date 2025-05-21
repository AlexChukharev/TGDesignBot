import logging
import json
import pickle

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utility.checkers import file_size_in_limit
from utility.tg_utility import (
    from_button_to_file, change_state_to_tags,
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
    choose_template_text_inner,
    choose_template_text_root,
    choose_category_callback,
    get_fonts_buttons_with_feedback,
    go_back_to_main_menu,
    go_back_to_main_menu_with_feedback,
    go_back_to_main_menu_with_feedback_and_freshness,
    ideas_final_buttons_with_feedback,
    tags_buttons,
    ideas_final_buttons
)
from ...keyboards import get_fonts_buttons, how_to_install_fonts_buttons

from Tree.ClassTree import Tree

from YandexDisk import get_download_link, get_file_size
from YandexDisk.YaDiskInfo import TemplateInfo

from DBHandler import (
    delete_template,
    get_template_id_by_name,
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


async def load_tree() -> Tree:
    return pickle.load(open("./Tree/ObjectTree.pkl", "rb"))


def get_disk_folder_name(query_type: str) -> str:
    """
        Получает название папки на Я. Диске, 
        в которой содержатся материалы, соответствующие типу запроса
    """
    if query_type in ['pres_templates', 'fonts']:
        return 'Шаблоны'
    if query_type == 'search_by_tags':
        return 'Advanced'
    if query_type == 'about_company':
        return 'Слайды о компании'
    if query_type == 'extra_assets':
        return 'Дополнительные материалы'


@router.callback_query(F.data == "pres_templates")
@router.callback_query(F.data == "fonts")
@router.callback_query(F.data == "search_by_tags")
@router.callback_query(F.data == "about_company")
@router.callback_query(F.data == "extra_assets")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
        TODO описание 
    """
    tree = await load_tree()
    config = await load_config()
    dist_indx = config['dist']

    await state.clear()
    await state.set_state(WalkerState.choose_button)
    type_file = await set_file_type(callback_query.data, state)

    root_child_list = tree.get_children(tree.root.path)
    print('root_child_list:', [node.name for node in root_child_list])
    path = [callback_query.data]

    indx_child = 0
    for child in root_child_list:
        print(f'child: {child.name}')
        if child.name == get_disk_folder_name(callback_query.data):
            break
        indx_child += 1
    path.append(root_child_list[indx_child])
    print(f'path: {path}')
    print('name: ', root_child_list[indx_child].name)
    print('path: ', root_child_list[indx_child].path)
    print('children: ', root_child_list[indx_child].children)
    child_list = tree.get_children(root_child_list[indx_child].path)
    print('children: ', [node.name for node in child_list])

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx

    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)


    await state.update_data(file_name_list=[])
    await update_user_info(state, path, 0, indx_list_end, False, child_list)

    reply_markup = await choose_category_callback(
        [node.name for node in child_list[indx_list_start:indx_list_end]],
        can_go_left,
        can_go_right,
        False,
        type_file
    )
    text = await choose_template_text_root(type_file)

    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def paginate_template_find(callback_query: CallbackQuery, state: FSMContext, direction: str):
    """
        TODO описание 
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
        [node.name for node in child_list[indx_list_start:indx_list_end]],
        can_go_left,
        can_go_right,
        can_go_back,
        type_file
    )
    text = await choose_template_text_inner(path[-1].name)

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
    await paginate_template_find(callback_query, state, "next")


@router.callback_query(WalkerState.choose_button, F.data == "prev")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes 'prev block of directories' action
    """
    await paginate_template_find(callback_query, state, "prev")


@router.callback_query(WalkerState.choose_button, F.data == "prev_dir")
async def prev_dir_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes 'prev directory' action
    """

    tree = await load_tree()
    config = await load_config()
    dist_indx = config['dist']

    user_info = await state.get_data()
    path = user_info['path']
    type_file = user_info['type_file']

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx

    cur_node_name = path.pop(-1)
    parent_path = path[-1].path if path else '/' # '/' + '/'.join(path) if path else '/'
    child_list = tree.get_children(parent_path)
    parent_name = path[-1].name if path else ''

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)

    reply_markup = await choose_category_callback(
        [node.name for node in child_list[indx_list_start:indx_list_end]],
        can_go_left,
        can_go_right,
        can_go_back,
        type_file
    )

    if parent_name == "root":
        logger.info('trying get the root folders')
        text = await error_text()
        await error_final(callback_query, text)
        return
    elif parent_name == 'Шаблоны':
        text = await choose_template_text_root(type_file)
    else:
        text = await choose_template_text_inner(parent_name)

    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list)


@router.callback_query(WalkerState.tags_search, F.data == "another_idea")
async def start_tags_search(callback_query: CallbackQuery, state: FSMContext):
    """
        TODO описание
    """
    state_info = await state.get_data()
    # tags_on_prev_step_dict = state_info['tags']
    # reply_markup = await tags_buttons(tags_on_prev_step_dict['sub_categories'], ('parent' in tags_on_prev_step_dict), False)  
    reply_markup = await ideas_final_buttons()
      
    reply_text = f"Если нет подходящего варианта, напиши {json.load(open('./CONFIG/config.json'))['owner']}"\
        "\n\nА пока, возможно, тебе поможет что-то из готового?"
    
    await callback_query.message.edit_text(
        text=reply_text,
        reply_markup=reply_markup
    )
    pass


@router.callback_query(WalkerState.tags_search, F.data == "ideas_from_start")
async def start_tags_search(callback_query: CallbackQuery, state: FSMContext):
    """
        TODO описание
    """

    reply_text = f'Что хочешь нарисовать?'
    try:
        with open("./CONFIG/tags_tree.json", "r") as tags_file:
            tags = json.load(tags_file)
    except Exception as e:
        logger.info('error while reading tags_tree.json')
        logger.info(e)
        text = await error_text()
        await error_final(callback_query, text)
        return
    await state.update_data(tags=tags)

    reply_markup = await tags_buttons(tags['sub_categories'], False, True)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def start_tags_search(callback_query: CallbackQuery, state: FSMContext, files_list):
    """
        TODO описание
    """

    file_name = files_list[0][2]
    file_path = files_list[0][1]
    reply_text = f'Отлично, делаем презентацию в шаблоне <b>{file_name[:-5]}</b>\nТеперь расскажи, какой слайд нам нужен'
    try:
        with open("./CONFIG/tags_tree.json", "r") as tags_file:
            tags = json.load(tags_file)
    except Exception as e:
        logger.info('error while reading tags_tree.json')
        logger.info(e)
        text = await error_text()
        await error_final(callback_query, text)
        return
    await change_state_to_tags(state, WalkerState.tags_search, files_list, [file_name], [file_path], tags)

    reply_markup = await tags_buttons(tags['sub_categories'], False, True)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def finish_tags_search(callback_query: CallbackQuery, state: FSMContext, tag: str):
    """
        TODO описание
    """

    # данные по шаблону
    files_list = await get_list_of_files(state)
    if not files_list:
        text = await error_text()
        await error_final(callback_query, text)
        return
    template_id = files_list[0][0]
    template_name = files_list[0][2]

    # получаем слайды по тегам
    slides_list = get_slides_by_tags_and_template_id([tag], template_id)
    if not len(slides_list):
        await error_final(callback_query, "Ничего не нашел :(")
        return
    try:
        await callback_query.message.edit_text(
            text='Принято. Сейчас подготовлю варианты и отправлю, это может занять пару минут'
        )
    except Exception as e:
        logger.info(e)

    # TODO все, что ниже – надо изучить, выглядит странно
    path_to_save = f'./Data/slides/{callback_query.message.from_user.id}.pptx'
    slide_info = SlideInfo(slides_list[0][0], ';'.join([tag]))
    for slide in slides_list[1:]:
        slide_info.add_id(slide[0])
    get_template = get_templates_by_index(template_id)
    template = get_template[0]
    template_info = TemplateInfo(template[2], template[1])
    slide_info.add_template_info(template_info)
    get_template_of_slides(path_to_save, slide_info)
    try:
        await send_file_from_local_for_query(callback_query, path_to_save, f'{tag} ({template_name[:-5]}).pptx')
    except Exception as e:
        logger.info('Error while send_file_from_local_for_query in finish_tags_search')
        logger.info(e)

    reply_markup = await ideas_final_buttons_with_feedback()
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Готово!\nОцени, пожалуйста, помогли ли тебе эти варианты",
        reply_markup=reply_markup
    )
    remove_template(path_to_save)


@router.callback_query(WalkerState.tags_search, F.data.isnumeric())
async def tags_search(callback_query: CallbackQuery, state: FSMContext):
    """
        TODO описание
    """

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
        reply_markup = await tags_buttons(new_tags, ('parent' in cur_tag), True)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=cur_tag['comment'],
            reply_markup=reply_markup
        )
    else:
        # дошли до листа => запускаем генерацию pptx
        if 'tag' in cur_tag:
            await finish_tags_search(callback_query, state, cur_tag['tag'])
        else:
            # такого вообще не должно быть
            logger.info('error in tags_search while getting tag')
            text = await error_text()
            await error_final(callback_query, text)


async def finish_template_search(callback_query: CallbackQuery, state: FSMContext):
    """
        TODO описание
    """

    user_info = await state.get_data()

    path = user_info['path']
    parent_name = path[-1].name

    files_list = await get_list_of_files(state)
    type_file = user_info['type_file']
    if not files_list:
        text = await error_text()
        await error_final(callback_query, text)
        return
    file_name = files_list[0][2]
    file_path = files_list[0][1]
    # TODO переводит состояние – переименовать
    await from_button_to_file(state, files_list, [file_name], WalkerState.choose_file, [file_path])
    await state.update_data(file_id=files_list[0][0])

    try:
        link = get_download_link(str(file_path) + '/' + str(file_name))
        file_size = get_file_size(str(file_path) + '/' + str(file_name))
    except Exception:
        reply_markup = await go_back_to_main_menu()
        template_info = TemplateInfo(str(file_name), str(file_path))
        template_id = get_template_id_by_name(template_info.path, template_info.name)
        delete_template(template_id)
        await try_to_delete_message(callback_query)
        text = await error_text()
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=text,
            reply_markup=reply_markup
        )
        return

    # TODO перенести отправку в отдельную функцию
    if file_size_in_limit(file_size):
        await callback_query.message.edit_text(
            text=f'Супер, отправляю! Это займет немного времени'
        )
        try:
            await download_with_link_query(callback_query, link, file_name)
            if type_file == "extra_assets":
                if "Логотипы" in parent_name:
                    reply_markup = await go_back_to_main_menu_with_feedback_and_freshness()
                else:
                    reply_markup = await go_back_to_main_menu_with_feedback()
                await try_to_delete_message(callback_query)
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text="Держи!\nКак посмотришь, оцени качество материала, пожалуйста 👀",
                    reply_markup=reply_markup
                )
            else:
                reply_markup = await get_fonts_buttons_with_feedback()
                await try_to_delete_message(callback_query)
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=f'Держи файл!\n'\
                        f'Как посмотришь, оцени качество материала, пожалуйста 👀\n\n'\
                        f'Если работаешь с шаблоном первый раз, не забудь установить корпоративные шрифты',
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


@router.callback_query(WalkerState.choose_button, F.data == "get_fonts_from_all_pres")
async def get_fonts_from_all_pres(callback_query: CallbackQuery, state: FSMContext):
    """
        Обработка конпки "скачать сразу все шрифты"
    """
        
    user_info = await state.get_data()
    path = '/'.join(user_info['path'][1:])
    
    # определяем сообщение и имя архива — отдельно обрабатываем корень
    item_name = ''
    try:
        if user_info['path'][-1] == 'Шаблоны':
            item_name = 'all'
            await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для всех наших презентаций, секунду...",
                    parse_mode=ParseMode.HTML
                )
        else:
            # отрезаем два символа – эмоджи и пробел
            item_name = user_info['path'][-1].name[2:]
            await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для <b>{item_name}</b>, секунду...",
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        logger.info(e)
    try:
        zip_name = f'Шрифты {item_name}'
        await start_send_fonts_for_query(callback_query, path, zip_name)
    except Exception as e:
        logger.info(e)
        return
    try:
        reply_markup = await how_to_install_fonts_buttons()
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text='Готово!',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.info(e)


@router.callback_query(WalkerState.choose_button, F.data.isnumeric())
async def navigate_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Имитация хождения по директориям при поиске материалов
    """
    tree = await load_tree()
    config = await load_config()

    user_info = await state.get_data()
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    indx_list_start = user_info['indx_list_start']
    path = user_info['path']

    indx_child = indx_list_start + int(callback_query.data) - 1
    path.append(child_list[indx_child])
    child_list = tree.get_children(child_list[indx_child].path)
    print([node.name for node in child_list])

    indx_list_start = 0
    dist_indx = config['dist']
    indx_list_end = dist_indx + indx_list_start

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list)

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
        # отдельно рассматривается случай со шрифтами – для них не хотим спускаться до уровня шаблонов — останавливаемся на уровне БЮ (4)
        if type_file == 'font' and len(path) == 4: # почему 4???
            await get_fonts_from_all_pres(callback_query, state)
        else:
            reply_markup = await choose_category_callback(
                [node.name for node in child_list[indx_list_start:indx_list_end]],
                can_go_left,
                can_go_right,
                can_go_back,
                type_file
            )
            text = await choose_template_text_inner(path[-1].name)
            await callback_query.message.edit_text(
                text=text, 
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
