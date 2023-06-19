from src.logger import initialize_logger
from dotenv import load_dotenv, find_dotenv

logger = initialize_logger(__name__)
_ = load_dotenv(find_dotenv())  # read local .env file


def main():
    logger.debug("I'm the main function!")
