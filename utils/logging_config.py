import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logging(bot_name: str) -> logging.Logger:
    """Set up logging configuration for a bot"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger(bot_name)
    logger.setLevel(logging.INFO)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        f'logs/{bot_name}.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_command(logger: logging.Logger, command: str, user: str, guild: str) -> None:
    """Log a command execution"""
    logger.info(f"Command '{command}' executed by {user} in {guild}")

def log_error(logger: logging.Logger, error: Exception, context: str) -> None:
    """Log an error with context"""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, status: int) -> None:
    """Log an API call"""
    logger.info(f"API Call - {api_name} - {endpoint} - Status: {status}") 