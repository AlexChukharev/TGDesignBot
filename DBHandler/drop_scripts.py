import psycopg2
from DBHandler.config import load_config


def drop_tables():
    """ Drop All tables in the database"""
    commands = (
        """drop table if exists fonts;""",
        """drop table if exists images;""",
        """drop table if exists slides""",
        """drop table if exists users""",
        """drop table if exists templates"""
    )
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
