import logging
import psycopg2
from DBHandler.config import load_config


logger = logging.getLogger(__name__)


def get_user_role(user_id) -> str | None:
    """
        Получает роль по id: user или admin.
        Сейчас не используется
    """
    sql = "select role from users where user_id = %s"

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
                if row is not None:
                    return row[0]
                else:
                    return None

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)


def is_user_admin(user_id) -> bool:
    """
        Проверяет админ ли пользователь.
        Сейчас не используется, тк нет админской панели
    """
    user_role = get_user_role(user_id)
    return user_role == "admin"


def __get_list_of_obj__(sql, *obj) -> list:
    config = load_config()
    list_of_obj = []
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, obj)
                row = cur.fetchone()

                while row is not None:
                    list_of_obj.append(row)
                    row = cur.fetchone()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)

    finally:
        return list_of_obj


def get_templates_from_directory(path: str) -> list:
    sql = "select * from templates where path = %s"
    return __get_list_of_obj__(sql, path)


def get_templates_by_index(index: str) -> list:
    sql = "select * from templates where template_id = %s"
    return __get_list_of_obj__(sql, index)


async def get_templates_from_child_directories(path: str) -> list:
    sql = "select * from templates where path like '%%' || %s || '%%'"
    return __get_list_of_obj__(sql, path)


def get_fonts_by_template_id(template_id: int) -> list:
    sql = "select * from fonts where template_id = %s"
    return __get_list_of_obj__(sql, template_id)


def get_fonts_from_directory(path: str) -> list:
    sql = "select * from fonts where path = %s"
    return __get_list_of_obj__(sql, path)


def get_fonts_from_child_directories(path: str) -> list:
    sql = "select * from fonts where path like '%%' || %s || '%%'"
    return __get_list_of_obj__(sql, path)


def get_slides_by_tags_and_template_id(tags: list, template_id: int) -> list:
    sql = "select * from slides where template_id = %s"
    list_of_slides = __get_list_of_obj__(sql, template_id)

    for idx in range(len(list_of_slides) - 1, -1, -1):
        for tag in tags:
            if not (tag == list_of_slides[idx][2]):
                list_of_slides.pop(idx)
                break
    return list_of_slides
