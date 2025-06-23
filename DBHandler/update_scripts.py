import logging
import psycopg2
from DBHandler.config import load_config


logger = logging.getLogger(__name__)


def update_user(user_id, role: str):
    """ Update user_role based on the vendor id """

    sql = """ update users
                set role = %s
                where user_id = %s"""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (role, user_id))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)


def update_path(old_path: str, new_path: str):
    sql_statements = [('templates', "UPDATE templates SET path = %s WHERE path = %s;"),
                    ('fonts', "UPDATE fonts SET path = %s WHERE path = %s;"),]
                    # ('slides', "UPDATE slides SET path = %s WHERE path = %s;")]
# добавить изменение имени

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for table, sql in sql_statements:
                    cur.execute(sql, (new_path, old_path))
                    logger.info(f"{table}: {cur.rowcount} строк обновлено.")
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Ошибка при обновлении путей: {error}")