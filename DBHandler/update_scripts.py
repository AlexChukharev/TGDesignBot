import logging
import psycopg2
from config import load_config


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
