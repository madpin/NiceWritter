import logging
import logging.handlers
import os


def initialize_logger(
    log_name: str,
    log_level: int = logging.DEBUG,
    log_format: str = "%(asctime)s [%(levelname)s] %(message)s",
    file_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    log_directory: str = "./logs",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Initializes a logger with a file handler that rotates based on file size.
    Args:
        log_name (str):
            The name of the logger.
        log_level (int):
            The logging level for the logger (default: logging.INFO).
        log_format (str):
            The log format for the screen handler
            (default: '%(asctime)s [%(levelname)s] %(message)s').
        file_format (str):
            The log format for the file handler
            (default: '%(asctime)s [%(levelname)s] %(name)s: %(message)s').
        log_directory (str):
            The directory where log files should be stored (default: './logs').
        max_bytes (int):
            The maximum size of each log file in bytes (default: 10MB).
        backup_count (int):
            The number of backup log files to keep (default: 5).
    Returns:
        logging.Logger: A configured instance of the Python logging.Logger class.
    """

    # Create a new logger with the specified name and level
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)

    # Remove any existing handlers from the logger
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Configure a console handler with the specified log format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_directory:
        # Ensure the log directory exists
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        # Configure a file handler with the
        # specified log format and rotation settings
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_directory, f"{log_name}.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
