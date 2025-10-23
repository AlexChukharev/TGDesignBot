import logging

def log_action_with_username(logger: logging.Logger, action: str, username: str, id: int):
    logger.info(f"Action: {action}, User: {username or 'unknown'}, ID: {id}")


def log_unauthorized(logger: logging.Logger, username: str, id: int):
    logger.info(f"Unauthorized user: {username or 'unknown'}, ID: {id}")

def log_sending(logger: logging.Logger, file: str):
    logger.info(f"Sending file: {file}")