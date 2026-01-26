"""Logger Manager - Centralized logging setup for all modules."""

import logging
from logging.handlers import RotatingFileHandler
import os

from .config import Config


class LoggerManager:
    """Centralized logger setup and management."""
    
    _config = None
    
    @classmethod
    def _get_config(cls):
        """Get or create config instance."""
        if cls._config is None:
            cls._config = Config()
        return cls._config
    
    @staticmethod
    def setup_logging(name: str = "app"):
        """Setup logging configuration.
        
        Args:
            name: Logger name (used for log file naming)
            
        Returns:
            Configured logger instance
        """
        config = LoggerManager._get_config()
        
        # Create logs folder if it doesn't exist
        logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Get log file path - try new method first, fall back to direct construction
        try:
            log_file = config.get_log_file_path(name=name)
        except (AttributeError, TypeError):
            log_file = os.path.join(logs_dir, f'{name}.log')
        
        logging_settings = config.get_logging_settings()

        # Setup logger
        logger = logging.getLogger(name)
        logger.setLevel(logging_settings['level'])

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=logging_settings['max_bytes'],
            backupCount=logging_settings['backup_count']
        )
        file_formatter = logging.Formatter(
            logging_settings['format'],
            datefmt=logging_settings['date_format']
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging_settings['level'])
        console_formatter = logging.Formatter(logging_settings['format'])
        console.setFormatter(console_formatter)
        logger.addHandler(console)

        return logger
