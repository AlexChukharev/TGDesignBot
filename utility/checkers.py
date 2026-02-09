import json
import os
import aiohttp

from CONFIG.config import CONFIG


staff_oauth_token = str(os.getenv('STAFF_OAUTH_TOKEN'))


def is_admin(id: int) -> bool:
    """
        Правда ли, что у пользователя с данным id есть админские права (на данный момент не используется)
    """
    with open("./CONFIG/admins.json", "r") as file:
        config = json.load(file)
        admins_list = config["admin_id"]
        return id in admins_list


def check_user_id_in_list(id: int) -> bool:
    """
        Проверяет, есть ли id пользователя в users.json
    """
    with open("./CONFIG/users.json", "r") as file:
        config = json.load(file)
        users_list = config["user_id"]
        return id in users_list


async def check_username_by_staff(username: str) -> bool:
    """
        Проверка, привязан ли тг-аккаунт username к стаффу
    """
    params = {
        'telegram_accounts.value_lower': username.lower(),
        '_fields': 'name',
    }
    headers = {
        'Authorization': f'OAuth {staff_oauth_token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://staff-api.yandex-team.ru/v3/persons', headers=headers, params=params
        ) as response:
            result = await response.json(content_type=None)
            return result['total'] > 0


async def is_user(id: int, username: str) -> bool:
    """
        Проверка, есть ли у пользователя доступ к боту
    """
    if username is None:
        return False

    if CONFIG["test_mode"]:
        return True
    else:
        return (await check_username_by_staff(username)) or check_user_id_in_list(id)


def file_size_in_limit(file_size: int) -> bool:
    """
        Проверка на размер файла — сможет ли телеграм его отправить (aug 2024)
        https://core.telegram.org/bots/api#senddocument
    """
    return file_size < (50 * 1024 * 1024)
