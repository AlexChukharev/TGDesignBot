import asyncio

from dotenv import load_dotenv

from DBHandler.initialize_database import initialize_database
from TelegramHandler import bot as TGbot
from Tree.ClassTree import tree
from YandexDisk.YaDiskHandler import create_tree

from messages.languages import load_user_langs


async def main():
    # Fill database + create tree with dir
    load_dotenv()
    load_user_langs()
    create_tree(tree)
    # Initialize DataBase.
    initialize_database()

    await TGbot.start_bot()

if __name__ == '__main__':
    asyncio.run(main())