import asyncio
import datetime
import pickle

from dotenv import load_dotenv

from DBHandler.initialize_database import initialize_database
from TelegramHandler import bot as TGbot
from Tree.ClassTree import Tree
from YandexDisk.YaDiskHandler import update_tree

from messages.languages import load_user_langs


async def main():
    # Fill database + create tree with dir
    load_dotenv()
    load_user_langs()
    tree = Tree()
    update_tree(tree, datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))
    with open("./Tree/ObjectTree.pkl", "wb") as fp:
        pickle.dump(tree, fp)
    # Initialize DataBase.
    initialize_database()

    await TGbot.start_bot()

if __name__ == '__main__':
    asyncio.run(main())
