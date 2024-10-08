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
    send_file_from_local_for_query, error_final, error_text
)

from ...keyboards.start_and_simple_button import (
    choose_template_text_inner,
    choose_template_text_root,
    choose_category_callback,
    go_back_to_main_menu,
    tags_buttons,
    choose_category_in_deadend_callback_for_fonts
)
from ...keyboards import get_fonts_buttons

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


class WalkerState(StatesGroup):
    # TODO не только это — изучить и добавить описание
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()
    tags_search = State()


async def load_config():
    with open("./config.json", "r") as file:
        return json.load(file)


async def load_tree() -> Tree:
    return pickle.load(open("./Tree/ObjectTree.pkl", "rb"))


@router.callback_query(F.data == "pres_templates")
@router.callback_query(F.data == "fonts")
@router.callback_query(F.data == "search_by_tags")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext) -> None:
    tree = await load_tree()
    config = await load_config()
    dist_indx = config['dist']

    await state.clear()
    await state.set_state(WalkerState.choose_button)
    type_file = await set_file_type(callback_query.data, state)

    child_list = tree.get_children(tree.root.name)

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx

    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)

    path = [callback_query.data]
    await state.update_data(file_name_list=[])
    await update_user_info(state, path, 0, indx_list_end, False, child_list)

    reply_markup = await choose_category_callback(
        child_list[indx_list_start:indx_list_end],
        can_go_left,
        can_go_right,
        False,
        type_file
    )
    text = await choose_template_text_root(type_file)

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )


# TODO проверить и написать описание
async def paginate_template_find(callback_query: CallbackQuery, state: FSMContext, direction: str):
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
        type_file
    )
    text = await choose_template_text_inner(path[-1])

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )

    await update_user_indx(state, indx_list_start, indx_list_end)


# Processes 'next block of directories' action
@router.callback_query(WalkerState.choose_button, F.data == "next")
async def next_template_find(callback_query: CallbackQuery, state: FSMContext):
    await paginate_template_find(callback_query, state, "next")


# Processes 'prev block of directories' action
@router.callback_query(WalkerState.choose_button, F.data == "prev")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    await paginate_template_find(callback_query, state, "prev")


# Processes 'prev directory' action
@router.callback_query(WalkerState.choose_button, F.data == "prev_dir")
async def prev_dir_template_find(callback_query: CallbackQuery, state: FSMContext):
    tree = await load_tree()
    config = await load_config()
    dist_indx = config['dist']

    user_info = await state.get_data()
    path = user_info['path']
    type_file = user_info['type_file']

    indx_list_start = 0
    indx_list_end = indx_list_start + dist_indx

    cur_node_name = path.pop(-1)
    parent_name = tree.get_parent(cur_node_name)
    child_list = tree.get_children(parent_name)

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)

    reply_markup = await choose_category_callback(
        child_list[indx_list_start:indx_list_end],
        can_go_left,
        can_go_right,
        can_go_back,
        type_file
    )
    if parent_name == 'root':
        text = await choose_template_text_root(type_file)
    else:
        text = await choose_template_text_inner(tree.get_parent(cur_node_name))

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list)


# TODO описание
async def start_tags_search(callback_query: CallbackQuery, state: FSMContext, files_list):
    file_name = files_list[0][2]
    file_path = files_list[0][1]
    reply_text = f'Отлично, делаем презентацию в шаблоне <b>{file_name}</b>\nТеперь расскажи, какой слайд нам нужен'
    try:
        with open("./tags_tree.json", "r") as tags_file:
            tags = json.load(tags_file)
    except:
        print('error while reading tags_tree.json')
        text = await error_text()
        await error_final(callback_query, text)
        return
    await change_state_to_tags(state, WalkerState.tags_search, files_list, [file_name], [file_path], tags)

    reply_markup = await tags_buttons(tags)
    await callback_query.message.delete()
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def finish_tags_search(callback_query: CallbackQuery, state: FSMContext, tag: str):
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
    except:
        # TODO обработать ошибки
        print('error2')

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
        await send_file_from_local_for_query(callback_query, path_to_save, f'{tag} ({template_name}).pptx')
    except:
        # TODO обработать ошибки
        print('err2')

    reply_markup = await go_back_to_main_menu()
    await callback_query.message.delete()
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Готово! Надеюсь, эти варианты тебе помогут",
        reply_markup=reply_markup
    )
    remove_template(path_to_save)


@router.callback_query(WalkerState.tags_search)
async def tags_search(callback_query: CallbackQuery, state: FSMContext):
    state_info = await state.get_data()
    tags_on_prev_step = state_info['tags']
    chosen_tag_id = int(callback_query.data) - 1
    cur_tag = tags_on_prev_step[chosen_tag_id]
    if 'sub_categories' in cur_tag:
        # не дошли до листа => ищем тег дальше
        new_tags = cur_tag['sub_categories']
        await state.update_data(tags=new_tags)
        reply_markup = await tags_buttons(new_tags)
        await callback_query.message.delete()
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
            print('error in tags_search while getting tag')
            text = await error_text()
            await error_final(callback_query, text)


# TODO описание
async def finish_template_search(callback_query: CallbackQuery, state: FSMContext):
    files_list = await get_list_of_files(state)
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
        print(file_size)
    except Exception:
        reply_markup = await go_back_to_main_menu()
        template_info = TemplateInfo(str(file_name), str(file_path))
        template_id = get_template_id_by_name(template_info.path, template_info.name)
        delete_template(template_id)
        await callback_query.message.delete()
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
            text=f'Супер, отправляю! Это займет минутку'
        )
        try:
            await download_with_link_query(callback_query, link, file_name)
            reply_markup = await get_fonts_buttons()
            await callback_query.message.delete()
            await callback_query.bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Держи файл! И не забудь проверить, что у тебя есть корпоративные шрифты",
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


# TODO переименовать + описание
async def finish_fonts_search(callback_query: CallbackQuery, state: FSMContext, can_go_back, files_list):
    reply_markup = await choose_category_in_deadend_callback_for_fonts(can_go_back)
    if files_list:
        text = f'\n Есть шрифты для <b>{files_list[0][2]}</b>\n'
        await callback_query.message.edit_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        text = await error_text()
        await error_final(callback_query, text)


@router.callback_query(WalkerState.choose_button, F.data == "get_fonts_from_all_pres")
async def get_fonts_from_all_pres(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    files_list = await get_list_of_files(state)
    path = '/'.join(user_info['path'][1:])
    zip_name = ''
    try:
        if len(files_list) == 1:
            if files_list[0][2] == 'fonts':
                await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для всех наших презентаций, секунду...",
                    parse_mode=ParseMode.HTML
                )
                zip_name = 'all'
            else:
                await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для <b>{files_list[0][2]}</b>, секунду...",
                    parse_mode=ParseMode.HTML
                )
                zip_name = files_list[0][2]
        else:
            if user_info['path'][-1] == 'fonts':
                await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для всех наших презентаций, секунду...",
                    parse_mode=ParseMode.HTML
                )
                zip_name = 'all'
            else:
                await callback_query.message.edit_text(
                    text=f"Отправляю шрифты для <b>{user_info['path'][-1]}</b>, секунду...",
                    parse_mode=ParseMode.HTML
                )
                zip_name = user_info['path'][-1]
    except:
        print('Proxy error')
    try:
        await start_send_fonts_for_query(callback_query, path, zip_name)
    except:
        return
    try:
        reply_markup = await go_back_to_main_menu()
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text='Готово!',
            reply_markup=reply_markup
        )
    except:
        print('Proxy error')


@router.callback_query(WalkerState.choose_button)
async def navigate_template_find(callback_query: CallbackQuery, state: FSMContext):
    tree = await load_tree()
    config = await load_config()

    user_info = await state.get_data()
    child_list = user_info['child_list']
    type_file = user_info['type_file']
    indx_list_start = user_info['indx_list_start']
    path = user_info['path']

    indx_child = indx_list_start + int(callback_query.data) - 1
    path.append(child_list[indx_child])
    child_list = tree.get_children(child_list[indx_child])

    indx_list_start = 0
    dist_indx = config['dist']
    indx_list_end = dist_indx + indx_list_start

    can_go_back = await check_back(path)
    can_go_right = await check_right(indx_list_end, len(child_list))
    can_go_left = await check_left(indx_list_start)
    await update_user_info(state, path, indx_list_start, indx_list_end, can_go_back, child_list)

    if not child_list:
        files_list = await get_list_of_files(state)
        if type_file == 'font':
            await finish_fonts_search(callback_query, state, can_go_back, files_list)
        if type_file == 'template':
            await finish_template_search(callback_query, state)
        if type_file == 'search_by_tags':
            await start_tags_search(callback_query, state, files_list)

    else:
        reply_markup = await choose_category_callback(
            child_list[indx_list_start:indx_list_end],
            can_go_left,
            can_go_right,
            can_go_back,
            type_file
        )
        text = await choose_template_text_inner(path[-1])
        await callback_query.message.edit_text(text=text, reply_markup=reply_markup)
