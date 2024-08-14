import psycopg2
from DBHandler.config import load_config


def get_user_role(user_id) -> str | None:
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
        print(error)


def is_user_admin(user_id) -> bool:
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
        print(error)

    finally:
        return list_of_obj


def get_templates_from_directory(path: str) -> list:
    sql = "select * from templates where path = %s"
    return __get_list_of_obj__(sql, path)


def get_template_id_by_name(path: str, name: str) -> int | None:
    sql = "select * from templates where path = %s and name = %s"
    result = __get_list_of_obj__(sql, path, name)
    if len(result) == 0:
        return None
    else:
        return result[0][0]


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


def get_images_by_template_id(template_id: int) -> list:
    sql = "select * from images where template_id = %s"
    return __get_list_of_obj__(sql, template_id)


def get_images_from_directory(path: str) -> list:
    sql = "select * from images where path = %s"
    return __get_list_of_obj__(sql, path)


def get_images_from_child_directories(path: str) -> list:
    sql = "select * from images where path like '%%' || %s || '%%'"
    return __get_list_of_obj__(sql, path)


def get_slides_by_tags_and_template_id(tags: list, template_id: int) -> list:
    sql = "select * from slides where template_id = %s"
    list_of_slides = __get_list_of_obj__(sql, template_id)

    for idx in range(len(list_of_slides) - 1, -1, -1):
        for tag in tags:
            if not (tag in list_of_slides[idx][2]):
                list_of_slides.pop(idx)
                break
    return list_of_slides


def get_all_tags_by_template_id(template_id: int) -> list:
    sql = "select tags from slides where template_id = %s"
    list_of_tags = __get_list_of_obj__(sql, template_id)
    set_tags = set()
    for slide in list_of_tags:
        list_of_tags_from_slide = slide[0].split(';')
        for tag in list_of_tags_from_slide:
            set_tags.add(tag)
    return list(set_tags)
