import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from TelegramHandler.handlers import (simple_func_handler,
                                      main_menu_handler,
                                      no_handled,
                                      feedback_handler)
from TelegramHandler.handlers.query_handlers import walker_menu as q_walker_menu
from TelegramHandler.handlers.query_handlers import choose_file as q_choose_file


async def setup_bot_commands(bot: Bot):
    bot_commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Нужна помощь")
    ]
    await bot.set_my_commands(bot_commands)


# Func for including router and start work.
async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_routers(
        # главное меню
        main_menu_handler.router,
        # поиск материалов
        q_walker_menu.router,
        q_choose_file.router,
        simple_func_handler.router,
        feedback_handler.router,
        # обработка потерянных и некорректных сообщений
        no_handled.router
    )

    # Start bot
    await setup_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, ssl=False)


async def start_bot():
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    handler = TimedRotatingFileHandler(filename='./logs/runtime.log', when='D', interval=1, backupCount=90, encoding='utf-8', delay=False)
    formatter = Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logger = logging.getLogger(__name__)
    logger.info('Logger has been setuped!')

    try:
        # Start bot
        await main()
    except:
        logger.info('Exit')


if __name__ == '__main__':
    start_bot()
