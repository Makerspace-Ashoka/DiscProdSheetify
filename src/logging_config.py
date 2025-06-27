import logging
import os
import sys

def setup_logging():
    """Configures the root logger for the entire application."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Define the logging format
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
    )

    # 1. Configure logging to a file (the ship's logbook)
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)

    # 2. Configure logging to the console (the ship's intercom)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)

    # 3. Get the root logger and add our handlers.
    # We configure the root logger so that any logger created with
    # logging.getLogger(__name__) will inherit this configuration.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)