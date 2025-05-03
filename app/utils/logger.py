import logging
import os
from logging.handlers import RotatingFileHandler
import sys


def configure_logger(
    app=None, console_output=True, file_output=False, log_level=logging.DEBUG
):
    """Configure logging for the application.

    Args:
        app: Flask application instance
        console_output: Whether to log to console (default: True)
        file_output: Whether to log to file (default: True)
        log_level: Overall logging level (default: INFO)
    """
    # Create logs directory if needed and file_output is enabled
    logs_dir = None
    if file_output:
        logs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
        )
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    verbose_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    simple_formatter = logging.Formatter("%(levelname)s ==----== %(message)s\n")

    handlers = []

    # Add console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        handlers.append(console_handler)

    # Add file handler if enabled
    if file_output and logs_dir:
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, "app.log"), maxBytes=10485760, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(verbose_formatter)
        root_logger.addHandler(file_handler)
        handlers.append(file_handler)

    # Configure Flask app logger if provided
    if app:
        app.logger.setLevel(log_level)
        # Remove default Flask handlers
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)

        # Add our handlers to the Flask logger
        for handler in handlers:
            app.logger.addHandler(handler)

        # Log app startup
        try:
            env_mode = app.config.get("ENV", "development")
            app.logger.info(f"Starting {app.name} in {env_mode} mode")
        except Exception as e:
            app.logger.info(f"Starting {app.name}")

    return root_logger
