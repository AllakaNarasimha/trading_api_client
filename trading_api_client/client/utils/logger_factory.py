"""Logger factory for context-aware logging.

Provides context-specific loggers for different modules like live data,
historical data, and option chain operations. Each context gets its own
log file while maintaining a consistent logging format.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from .config import Config


class LoggerFactory:
    """Create and manage loggers for different contexts."""
    
    _loggers = {}
    _config = Config()
    
    @classmethod
    def get_logger(cls, context: str = None) -> logging.Logger:
        """Get or create logger for a specific context.
        
        Args:
            context: One of 'live', 'history', 'option-chain', or None (default)
                    If None, returns the default 'price_watcher' logger
        
        Returns:
            Configured logger instance with context-specific log file
            
        Example:
            >>> logger = LoggerFactory.get_logger('live')
            >>> logger.info("Live data fetch started")
            # Logs to: option_chain_monitor_api_live.log
        """
        # Use 'price_watcher' as default context
        if context is None:
            context = 'price_watcher'
        
        # Return cached logger if already created
        if context in cls._loggers:
            return cls._loggers[context]
        
        # Create new logger with context name
        logger = logging.getLogger(context)
        
        # Skip configuration if already configured
        if logger.handlers:
            cls._loggers[context] = logger
            return logger
        
        # Configure logging level
        logger.setLevel(cls._config.LOG_LEVEL)
        
        # Get log file path with context name
        log_file = cls._config.get_log_file_path(context)
        
        # Get logging settings from config
        logging_settings = cls._config.get_logging_settings()
        
        # Setup file handler with rotation
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
        
        # Setup console handler
        console = logging.StreamHandler()
        console.setLevel(logging_settings['level'])
        console_formatter = logging.Formatter(logging_settings['format'])
        console.setFormatter(console_formatter)
        logger.addHandler(console)
        
        # Cache the logger
        cls._loggers[context] = logger
        return logger
    
    @classmethod
    def clear_cache(cls):
        """Clear cached loggers. Useful for testing."""
        cls._loggers.clear()
