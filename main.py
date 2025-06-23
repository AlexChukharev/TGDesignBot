import asyncio
import datetime
import pickle
import json

# from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from DBHandler.initialize_database import initialize_database
from TelegramHandler import bot as TGbot
from Tree.ClassTree import Tree
from YandexDisk.UpdateDisk import update_tree_and_db
from YandexDisk.YaDiskHandler import create_tree


async def main():
    # Fill database + create tree with dir
    load_dotenv()

    TEST_MODE = json.load(open("./CONFIG/config.json"))["test_mode"]
    ROOT = 'disk:/TelegramBotFastTest' if TEST_MODE else 'disk:/TelegramBot'

    tree = Tree()
    tree.make_root('', ROOT)
    
    # update_tree(tree, datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), True)
    
    with open("./Tree/ObjectTree.pkl", "wb") as fp:
        pickle.dump(tree, fp)
    # Initialize DataBase.
    initialize_database()

    await update_tree_and_db()

    # AutoUpdating information from YaDisk every 12 hours.
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(update_tree_and_db, "interval", hours=12)
    # scheduler.start()

    scheduler = AsyncIOScheduler()
    if TEST_MODE:
        scheduler.add_job(update_tree_and_db, "interval", minutes=5)
    else:
        scheduler.add_job(update_tree_and_db, "interval", hours=12)
    scheduler.start()

    await TGbot.start_bot()

if __name__ == '__main__':
    asyncio.run(main())
