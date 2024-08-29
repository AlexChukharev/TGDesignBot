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


# Check if the file is small enough to send via Telegram
# The limit is 50Mb (aug 2024)
# https://core.telegram.org/bots/api#senddocument
# TODO проверить, где еще она нужна проверка
def file_size_in_limit(file_size: int) -> bool:
    return file_size < (50 * 1024 * 1024)
