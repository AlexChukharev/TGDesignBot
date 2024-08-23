import json


def is_admin(id: int) -> bool:
    with open("admins.json", "r") as file:
        config = json.load(file)
        admins_list = config["admin_id"]
        return id in admins_list


def is_user(id: int) -> bool:
    with open("users.json", "r") as file:
        config = json.load(file)
        users_list = config["user_id"]
        return id in users_list