import logging
import psycopg2
from DBHandler.config import load_config


logger = logging.getLogger(__name__)


def create_tables():
    """ Create tables in the PostgreSQL database"""
    commands = (
        """ set statement_timeout = 0; """,
        """ set lock_timeout = 0; """,
        """ set client_encoding = 'UTF8'; """,
        """ set standard_conforming_strings = on; """,
        """ set check_function_bodies = false; """,
        """ set client_min_messages = warning; """,
        """ set default_tablespace = ''; """,
        """
            create table if not exists users (
                user_id bigint primary key,
                role text check (role in ('user', 'admin'))
            );
        """,
        """ create table if not exists templates (
                template_id serial primary key,
                path text not null,
                name text not null
            );
        """,
        """
            create table if not exists fonts (
                font_id serial primary key,
                path text not null,
                template_id serial,
                name text not null,
                foreign key (template_id) references templates(template_id) on delete cascade
            );
        """,
        """
            create table if not exists slides (
                slide_id int,
                template_id serial,
                foreign key (template_id) references templates(template_id) on delete cascade,
                tags text
            );
        """
    )
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the creating table statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        logger.info(error)


if __name__ == "__main__":
    create_tables()
