import json

from utility.tg_utility import can_go_right as check_right, \
    download_with_link_query, send_file_from_local_for_query
from utility.tg_utility import can_go_left as check_left
from utility.tg_utility import update_indx as update_user_indx
from DBHandler import (get_fonts_by_template_id,
                                   get_all_tags_by_template_id,
                                   get_slides_by_tags_and_template_id,
                                   get_templates_by_index, delete_template, get_template_id_by_name)
from YandexDisk.YaDiskInfo import TemplateInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from ...keyboards import choose_category_text, error_in_send_file, main_menu_kb_query, choose_tags_query, \
    choose_one_file
from ...keyboards.choose_file_keyboard import choose_file_kb_query, download_file_query, work_with_tags_query
from pptxHandler import get_template_of_slides, SlideInfo, remove_template
from YandexDisk import get_download_link

router = Router()


class WalkerState(StatesGroup):
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()
    choose_tags = State()


@router.callback_query(WalkerState.choose_file, F.data == "next")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_indx = config['dist']

        user_info = await state.get_data()
        indx_list_end = user_info['indx_list_end']
        file_name_list = user_info['file_name_list']
        paths_list = user_info['paths_list']

        indx_list_start = indx_list_end
        indx_list_end = indx_list_end + dist_indx

        can_go_right = await check_right(indx_list_end, len(file_name_list))
        can_go_left = await check_left(indx_list_start)

        reply_markup = await choose_file_kb_query(file_name_list[indx_list_start:indx_list_end], can_go_left,
                                                  can_go_right)
        text = await choose_one_file(
            file_name_list[indx_list_start:indx_list_end],
            paths_list[indx_list_start:indx_list_end]
        )

        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

        await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_file, F.data == "prev")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_indx = config['dist']

        user_info = await state.get_data()
        indx_list_start = user_info['indx_list_start']
        indx_list_end = user_info['indx_list_end']
        file_name_list = user_info['file_name_list']
        paths_list = user_info['paths_list']

        indx_list_start -= dist_indx
        indx_list_end -= dist_indx

        can_go_right = await check_right(indx_list_end, len(file_name_list))
        can_go_left = await check_left(indx_list_start)

        reply_markup = await choose_file_kb_query(file_name_list[indx_list_start:indx_list_end], can_go_left,
                                                  can_go_right)
        text = await choose_one_file(
            file_name_list[indx_list_start:indx_list_end],
            paths_list[indx_list_start:indx_list_end]
        )

        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

        await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_file, F.data == "get_fonts")
@router.callback_query(WalkerState.choose_tags, F.data == "get_fonts")
async def get_fonts(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    template_id = user_info["file_id"]
    list_fonts = get_fonts_by_template_id(template_id)

    if len(list_fonts) == 0:
        reply_markup = await error_in_send_file()
        await callback_query.message.edit_text(
            text="Для данной презентации нет шрифтов!",
            reply_markup=reply_markup
        )
        return

    try:
        await callback_query.message.edit_text(
            text="Дождитесь полной отправки шрифтов..."
        )
    except:
        print('Error')
    try:
        path = list_fonts[0][1] + '/' + list_fonts[0][3]
        link = get_download_link(path)
        await download_with_link_query(callback_query, link, 'fonts.zip')
        reply_markup = main_menu_kb_query()
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Все шрифты отправлены!",
            reply_markup=reply_markup
        )
    except:
        pass


@router.callback_query(WalkerState.choose_file, F.data == "install_fonts_help")
@router.callback_query(WalkerState.choose_tags, F.data == "install_fonts_help")
async def send_info(callback_query: CallbackQuery):
    try:
        await callback_query.message.edit_text(
            text='Дождитесь отправки файла...'
        )
    except:
        print('Proxy error')
    path = './Data/Appdata/00 How to install fonts.pdf'
    await send_file_from_local_for_query(callback_query, path, 'How to install fonts.pdf')
    reply_markup = await error_in_send_file()
    await callback_query.message.delete()
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Это вам поможет!',
        reply_markup=reply_markup
    )


@router.callback_query(WalkerState.choose_tags, F.data == "next")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_indx = config['dist']

        user_info = await state.get_data()
        user_tags = user_info['user_tags']
        indx_list_end = user_info['indx_list_end']
        list_tags = user_info['list_tags']

        indx_list_start = indx_list_end
        indx_list_end = indx_list_end + dist_indx

        can_go_right = await check_right(indx_list_end, len(list_tags))
        can_go_left = await check_left(indx_list_start)
        text = await choose_tags_query(list_tags[indx_list_start:indx_list_end])
        reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end],
                                                  can_go_left,
                                                  can_go_right,
                                                  state)
        await callback_query.message.edit_text(
            text=f"Введите ваши теги через ';' или Выберите их из предложенных ниже \n Ваши теги: {user_tags} \n" + text,
            reply_markup=reply_markup
        )
        await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_tags, F.data == "prev")
async def first_depth_template_find(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_indx = config['dist']

        user_info = await state.get_data()
        user_tags = user_info['user_tags']
        indx_list_start = user_info['indx_list_start']
        indx_list_end = user_info['indx_list_end']
        list_tags = user_info['list_tags']

        indx_list_start -= dist_indx
        indx_list_end -= dist_indx

        can_go_right = await check_right(indx_list_end, len(list_tags))
        can_go_left = await check_left(indx_list_start)
        text = await choose_tags_query(list_tags[indx_list_start:indx_list_end])
        reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end],
                                                  can_go_left,
                                                  can_go_right,
                                                  state)
        await callback_query.message.edit_text(
            text=f"Введите ваши теги через ';' или Выберите их из предложенных ниже \n Ваши теги: {user_tags} \n" + text,
            reply_markup=reply_markup
        )

        await update_user_indx(state, indx_list_start, indx_list_end)


@router.callback_query(WalkerState.choose_tags, F.data == "clear_tags")
async def clear_tags(callback_query: CallbackQuery, state: FSMContext):
    # Clear user_tags
    await state.update_data(user_tags=[])
    # Default output
    user_info = await state.get_data()
    user_tags = user_info['user_tags']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    list_tags = user_info['list_tags']

    can_go_right = await check_right(indx_list_end, len(list_tags))
    can_go_left = await check_left(indx_list_start)

    reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end], can_go_left, can_go_right,
                                              state)

    text = f"Введите ваши теги через ';' или Выберите их из предложенных ниже \n Ваши теги: {user_tags} \n"
    text += await choose_tags_query(list_tags[indx_list_start:indx_list_end])
    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )


@router.callback_query(WalkerState.choose_tags, F.data == "find_with_tags")
async def clear_tags(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    user_tags = user_info['user_tags']
    template_id = user_info['file_id']

    slides_list = get_slides_by_tags_and_template_id(user_tags, template_id)
    # No need slides
    if len(slides_list) == 0:
        indx_list_start = user_info['indx_list_start']
        indx_list_end = user_info['indx_list_end']
        list_tags = user_info['list_tags']

        can_go_right = await check_right(indx_list_end, len(list_tags))
        can_go_left = await check_left(indx_list_start)

        reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end],
                                                  can_go_left,
                                                  can_go_right,
                                                  state)

        try:
            await callback_query.message.answer(
                text=f'Нет слайдов в данной презентации, содержащих следующие теги: \n {user_tags}',
                reply_markup=reply_markup
            )
        except:
            print('error')
    else:
        try:
            await callback_query.message.edit_text(
                text='Дождитесь, пока файл загрузится...'
            )
        except:
            print('error2')
        path_to_save = f'./Data/slides/{callback_query.message.from_user.id}.pptx'
        slide_info = SlideInfo(slides_list[0][0], ';'.join(user_tags))
        for slide in slides_list[1:]:
            slide_info.add_id(slide[0])
        get_template = get_templates_by_index(template_id)
        template = get_template[0]
        template_info = TemplateInfo(template[2], template[1])
        slide_info.add_template_info(template_info)
        get_template_of_slides(path_to_save, slide_info)
        try:
            await send_file_from_local_for_query(callback_query, path_to_save, 'Slides.pptx')
        except:
            print('err2')
        reply_markup = download_file_query()
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Ваш файл успешно загружен!",
            reply_markup=reply_markup
        )
        remove_template(path_to_save)


@router.message(WalkerState.choose_tags)
async def choose_tags(message: Message, state: FSMContext):
    user_info = await state.get_data()
    user_tags = user_info['user_tags']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    list_tags = user_info['list_tags']
    print(list_tags)

    input_tags = message.text.split(';')
    for tag in input_tags:
        if tag in user_tags:
            await message.answer(
                text=f'Тег "{tag}" уже добавлен'
            )
            continue
        if tag not in list_tags:
            await message.answer(
                text=f'Извините, тега "{tag}" в презентации нет'
            )
        else:
            await message.answer(
                text=f'Тег "{tag}" добавлен'
            )
            user_tags.append(tag)
    can_go_right = await check_right(indx_list_end, len(list_tags))
    can_go_left = await check_left(indx_list_start)
    await state.update_data(user_tags=user_tags)

    reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end], can_go_left, can_go_right,
                                              state)
    text = await choose_tags_query(list_tags[indx_list_start:indx_list_end])
    await message.answer(
        text=f"Введите ваши теги через ';' или Выберите их из предложенных ниже \n Ваши теги: {user_tags} \n" + text,
        reply_markup=reply_markup
    )


@router.callback_query(WalkerState.choose_tags)
async def choose_tags(callback_query: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    user_tags = user_info['user_tags']
    indx_list_start = user_info['indx_list_start']
    indx_list_end = user_info['indx_list_end']
    list_tags = user_info['list_tags']
    print(list_tags)
    tag_index = indx_list_start + int(callback_query.data) - 1
    tag = list_tags[tag_index]

    text = ""

    if tag not in user_tags:
        user_tags.append(list_tags[tag_index])
        text += f"Тег {tag} успешно добавлен! \n"
    else:
        text += "Данный тег уже есть в списке! \n"

    text += f"Введите ваши теги через ';' или Выберите их из предложенных ниже \n Ваши теги: {user_tags} \n"
    can_go_right = await check_right(indx_list_end, len(list_tags))
    can_go_left = await check_left(indx_list_start)
    await state.update_data(user_tags=user_tags)

    reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end], can_go_left, can_go_right,
                                              state)
    text += await choose_tags_query(list_tags[indx_list_start:indx_list_end])
    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_markup
    )


@router.callback_query(WalkerState.choose_file)
async def choose_category(callback_query: CallbackQuery, state: FSMContext):
    with open("./config.json", "r") as file:
        config = json.load(file)
        dist_index = config['dist']
        user_info = await state.get_data()
        file_name_list = user_info['file_name_list']
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
            except Exception:
                await callback_query.message.edit_text(
                    text="Не удалось найти данный файл, возможно он был перемещён или удалён."
                )
                template_info = TemplateInfo(str(file_name), str(file_path))
                template_id = get_template_id_by_name(template_info.path, template_info.name)
                delete_template(template_id)
                return

            await callback_query.message.edit_text(
                text="Ваш файл загружается..."
            )
            try:
                await download_with_link_query(callback_query, link, file_name)
                reply_markup = download_file_query()
                await callback_query.message.delete()
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text="Ваш файл успешно загружен!",
                    reply_markup=reply_markup
                )

            except:
                reply_markup = await error_in_send_file()
                await callback_query.message.delete()
                await callback_query.bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=f"Ошибка времени ожидания, сообщите о проблеме {json.load(open('./config.json'))['email']}, "
                         f"или попробуйте позже",
                    reply_markup=reply_markup
                )

        if type_file == 'slide':
            await state.clear()
            await state.set_state(WalkerState.choose_tags)

            list_tags = get_all_tags_by_template_id(file_id)
            try:
                list_tags.remove('')
            except:
                print('No empty tags')
            await state.update_data(list_tags=list_tags)
            await state.update_data(user_tags=[])
            await state.update_data(file_id=file_id)

            indx_list_start = 0
            indx_list_end = indx_list_start + dist_index
            can_go_right = await check_right(indx_list_end, len(list_tags))
            can_go_left = await check_left(indx_list_start)
            await state.update_data(indx_list_start=indx_list_start)
            await state.update_data(indx_list_end=indx_list_end)

            await update_user_indx(state, indx_list_start, indx_list_end)

            reply_markup = await work_with_tags_query(list_tags[indx_list_start:indx_list_end], can_go_left,
                                                      can_go_right, state)
            text = await choose_category_text(list_tags[indx_list_start:indx_list_end])
            await callback_query.message.edit_text(
                text="Введите ваши теги через ';' или Выберите их из предложенных ниже \n \n" + text,
                reply_markup=reply_markup
            )
        if type_file == 'font':
            font_name = get_fonts_by_template_id(file_id)
            if len(font_name) == 0:
                reply_markup = await error_in_send_file()
                await callback_query.message.edit_text(
                    text="Для данной презентации нет шрифтов!",
                    reply_markup=reply_markup
                )
            try:
                link = get_download_link(file_path + '/' + font_name[0][3])
            except Exception:
                await callback_query.message.edit_text(
                    text="Не удалось найти данный файл, возможно он был перемещён или удалён."
                )
                return
            reply_markup = download_file_query()
            try:
                await callback_query.message.edit_text(
                    text="Дождитесь полной отправки шрифтов..."
                )
            except:
                print('Error')
            try:
                await download_with_link_query(callback_query, link, 'fonts.zip')
                reply_markup = await error_in_send_file()
                await callback_query.message.delete()
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="Все шрифты отправлены!",
                    reply_markup=reply_markup
                )
            except:
                print('Font send error')
