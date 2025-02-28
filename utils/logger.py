"""
Logging Module for Traffic Bot Application.

This module provides standardized logging functionality for all bots in the traffic-bot application,
with support for different log levels, daily log rotation, and output to project logs directory.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any


class LoggerConfig:
    """Configuration settings for the logger module."""

    # Default log settings
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Environment variable names for configuration
    ENV_LOG_LEVEL = "LOG_LEVEL"
    ENV_CONSOLE_OUTPUT = "CONSOLE_OUTPUT"

    @classmethod
    def get_log_level(cls) -> int:
        """
        Get log level from environment variable or use default.

        Returns:
            logging level constant
        """
        level_name = os.environ.get(cls.ENV_LOG_LEVEL, "INFO").upper()
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(level_name, cls.DEFAULT_LOG_LEVEL)

    @classmethod
    def get_log_directory(cls) -> str:
        """
        Get log directory path within the project.

        Returns:
            Path to the log directory
        """
        # Get project root directory (assuming this module is in utils/)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Define logs directory
        logs_dir = os.path.join(project_root, 'logs')

        # Create logs directory if it doesn't exist
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir, exist_ok=True)
            except (PermissionError, OSError) as e:
                print(f"Warning: Could not create logs directory {logs_dir}: {str(e)}")
                # Fall back to current directory
                logs_dir = os.getcwd()

        return logs_dir

    @classmethod
    def should_output_to_console(cls) -> bool:
        """
        Check if logs should also be output to console.

        Returns:
            True if console output is enabled, False otherwise
        """
        return os.environ.get(cls.ENV_CONSOLE_OUTPUT, "True").lower() in ("true", "yes", "1")


class BotLogger:
    """Logger class for traffic bots with configurable output and daily rotation."""

    # Store configured loggers to avoid duplicate setup
    _loggers = {}

    # Set up the base configuration - will be done only once
    _is_initialized = False

    @classmethod
    def _initialize_base_config(cls):
        """
        Initialize base logging configuration if not already done.
        This should be done only once for the application.
        """
        if cls._is_initialized:
            return

        # Disable the propagation of logs to the root logger
        logging.getLogger().handlers = []

        # Set root logger level
        logging.getLogger().setLevel(LoggerConfig.get_log_level())

        # Mark as initialized
        cls._is_initialized = True

    @classmethod
    def setup_logger(cls, logger_name: str) -> logging.Logger:
        """
        Set up and configure a logger with the given name.

        Args:
            logger_name: Name of the logger

        Returns:
            Configured logger instance
        """
        # Initialize base config if needed
        cls._initialize_base_config()

        # Return existing logger if already set up
        if logger_name in cls._loggers:
            return cls._loggers[logger_name]

        # Get configuration
        log_level = LoggerConfig.get_log_level()
        logs_dir = LoggerConfig.get_log_directory()
        console_output = LoggerConfig.should_output_to_console()

        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        # Remove existing handlers if any
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Prevent logs from propagating to the root logger
        logger.propagate = False

        # Create formatter
        formatter = logging.Formatter(
            fmt=LoggerConfig.DEFAULT_LOG_FORMAT,
            datefmt=LoggerConfig.DEFAULT_DATE_FORMAT
        )

        # Add daily rotating file handler
        try:
            # Use TimedRotatingFileHandler for daily rotation
            log_file_path = os.path.join(logs_dir, f"{logger_name}.log")
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=log_file_path,
                when='midnight',  # Rotate at midnight
                interval=1,       # One day per file
                backupCount=30,   # Keep 30 days of logs
                encoding='utf-8'
            )
            # Set suffix for the rotated file to include date
            file_handler.suffix = "%Y-%m-%d"

            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not set up file handler: {str(e)}")

        # Add console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Store the logger
        cls._loggers[logger_name] = logger

        return logger


def log_message(bot_name: str, message: str, level: str = "INFO") -> None:
    """
    Log a message with the specified bot name and level.

    This function is the main entry point for logging in the application.
    It creates or retrieves a logger for the specified bot and logs the message
    at the specified level.

    Args:
        bot_name: Name of the bot generating the log (used as logger name)
        message: Message to log
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = BotLogger.setup_logger(bot_name)

    # Map level string to logging method
    log_methods = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical
    }

    # Get the appropriate logging method or default to info
    log_method = log_methods.get(level.upper(), logger.info)

    # Call the logging method with the message
    log_method(message)

    # Print to console for backward compatibility if console output is disabled
    if not LoggerConfig.should_output_to_console():
        print(f"[{bot_name}] {message}")
