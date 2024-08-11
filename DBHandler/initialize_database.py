import json
from DBHandler.create_tables import create_tables
from DBHandler.fill_database import fill_database
from YandexDisk.YaDiskHandler import get_all_files_in_disk
from DBHandler.drop_scripts import drop_tables
from DBHandler.insert_scripts import insert_many_users


def initialize_database() -> None:
    drop_tables()
    create_tables()
    with open("./admins.json", "r") as admins_file:
        config = json.load(admins_file)

    admins = config["admin_id"]
    for i in range(0, len(admins)):
        admins[i] = [admins[i], "admin"]

    if len(admins) != 0:
        insert_many_users(admins)
    fill_database(get_all_files_in_disk())
