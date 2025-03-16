import logging
import psycopg2
from DBHandler.config import load_config


logger = logging.getLogger(__name__)


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        logger.info(error)


if __name__ == '__main__':
    config = load_config()
    connect(config)