import json
import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from TelegramHandler.keyboards.buttons import get_fonts_buttons, go_back_to_main_menu, ideas_final_buttons
from utility.tg_utility import error_final, error_text, get_list_of_files, try_to_delete_message


router = Router()
logger = logging.getLogger(__name__)


def thanks_for_good_feedback_text() -> str:
    return "Спасибо за фидбек ❤️"


def thanks_for_bad_feedback_text() -> str:
    return f"Спасибо за фидбек ❤️\nБуду рад, если поделишься впечатлениями подробнее в чате {json.load(open('./CONFIG/config.json'))['owner']}"


def thanks_for_feedback_text(type_file: str, score: str) -> str:
    if score == "feedback_bad":
        text = thanks_for_bad_feedback_text()
    else:
        text = thanks_for_good_feedback_text()
            
    if type_file != "extra_assets" and type_file != "search_by_tags":
        text += "\n\nИ напоминаю про шрифты"
    return text


@router.callback_query(F.data == "feedback_great")
@router.callback_query(F.data == "feedback_good")
@router.callback_query(F.data == "feedback_bad")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes feedback buttons and saves to feedback.csv
    """

    files_list = await get_list_of_files(state)
    user_info = await state.get_data()
    type_file = user_info['type_file']
    if not files_list:
        text = await error_text()
        await error_final(callback_query, text)
        return
    file_name = files_list[0][2]
    file_path = files_list[0][1]

    feedback_text = str(file_path) + '/' + str(file_name) + ", " + callback_query.data + ", " + \
            callback_query.from_user.username + ", " + datetime.today().strftime('%Y-%m-%d')

    reply_text = thanks_for_feedback_text(type_file, callback_query.data)
    if type_file == "extra_assets":
        reply_markup = await go_back_to_main_menu()
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
    elif type_file == "search_by_tags":
        feedback_text += ", " + user_info['tags']['tag']
        reply_markup = await ideas_final_buttons()
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
    else:
        reply_markup = await get_fonts_buttons()
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )

    with open("feedback.csv", "a") as file:
        file.write(feedback_text + "\n")
    logger.info(feedback_text)


@router.callback_query(F.data == "freshness_feedback")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes freshness feedback button. Used for Logo files
    """
    
    reply_markup = await go_back_to_main_menu()
    reply_text = f"Обязательно напиши об этом {json.load(open('./CONFIG/config.json'))['owner']}!"
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        reply_markup=reply_markup
    )
