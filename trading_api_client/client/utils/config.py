"""
Configuration management for Option Chain Monitor.
Loads configuration from XML file with environment variable overrides.
"""

import logging
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class Config:
    """Configuration management class for option chain monitor."""
    
    _instance = None  # Singleton instance
    
    def __new__(cls, config_file: str = 'config.xml'):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file: str = 'config.xml'):
        """Initialize configuration with default values.
        
        Args:
            config_file: Path to XML configuration file
        """
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        # Default symbols with their poll intervals and strikes
        # Format: {symbol: {'poll_seconds': [list], 'strikes': int}}
        self.DEFAULT_SYMBOL_CONFIG = {
            "NSE:NIFTY50-INDEX": {"poll_seconds": [0, 30], "strikes": 15},      # Every 30 seconds, 15 strikes
            "NSE:NIFTYBANK-INDEX": {"poll_seconds": [0, 30], "strikes": 15},    # Every 30 seconds, 15 strikes
        }
        
        # Option monitor enable/disable
        self.OPTION_MONITOR_ENABLED = True
        
        # Cutoff time settings
        self.CUTOFF_ENABLED = False
        self.CUTOFF_HOUR = 15  # 3 PM
        self.CUTOFF_MINUTE = 30
        
        try:
            config_dir_file = 'config.dir'
            with open(config_dir_file, 'r') as f:
                config_dir = f.read().strip()
            config_file = os.path.join(config_dir, 'config.xml')
        except FileNotFoundError:
            # Default to config.xml in the same directory as this script
            config_file = 'config.xml'
        except Exception as e:
            logger.error(f"Error reading config.dir: {e}")
            config_file = 'config.xml'

        self.config_file = config_file

        logger.info(f"Using config file: {self.config_file}")
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from XML file with fallback to defaults."""
        # Set defaults first
        self.OPTION_MONITOR_ENABLED = True
        self.DEFAULT_STRIKES = 15
        self.API_HOST = '0.0.0.0'
        self.API_PORT = 5000
        self.AUTO_START = True
        self.MAX_SYMBOLS = 30
        self.MIN_POLL_INTERVAL = 5  # Minimum seconds between polls
        self.OPTION_CHAIN_FETCH_DURATION = 1  # Default 1 second between polls
        self.HEALTH_CHECK_INTERVAL = 300  # Default 5 minutes (300 seconds)
        self.LOG_LEVEL = logging.INFO
        self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
        self.LOG_BACKUP_COUNT = 5
        
        # Historical data settings
        self.HISTORICAL_DATA_ENABLED = False
        self.HISTORICAL_BACKDAYS = 30
        self.HISTORICAL_DURATION = 5
        self.HISTORICAL_CSV_EXPORT_ENABLED = False
        self.HISTORICAL_SYMBOLS = []  # List of symbols to fetch historical data for
        
        # Live data settings
        self.LIVE_DATA_ENABLED = False
        self.LIVE_DATA_CSV_EXPORT_ENABLED = False
        self.LIVE_DATA_SYMBOLS = []  # List of symbols to stream live prices for
        
        # Try to load from XML file
        if os.path.exists(self.config_file):
            try:
                tree = ET.parse(self.config_file)
                root = tree.getroot()
                
                # Look for option_monitor section
                monitor_section = root.find('option_monitor')
                if monitor_section is not None:
                    # Enabled/disabled setting
                    if monitor_section.find('enabled') is not None:
                        self.OPTION_MONITOR_ENABLED = monitor_section.find('enabled').text.lower() == 'true'
                    # API settings
                    if monitor_section.find('api_host') is not None:
                        self.API_HOST = monitor_section.find('api_host').text or self.API_HOST
                    if monitor_section.find('api_port') is not None:
                        self.API_PORT = int(monitor_section.find('api_port').text or self.API_PORT)
                    if monitor_section.find('auto_start') is not None:
                        self.AUTO_START = monitor_section.find('auto_start').text.lower() == 'true'
                    if monitor_section.find('default_strikes') is not None:
                        self.DEFAULT_STRIKES = int(monitor_section.find('default_strikes').text or self.DEFAULT_STRIKES)
                    if monitor_section.find('max_symbols') is not None:
                        self.MAX_SYMBOLS = int(monitor_section.find('max_symbols').text or self.MAX_SYMBOLS)
                    if monitor_section.find('option_chain_fetch_duration') is not None:
                        self.OPTION_CHAIN_FETCH_DURATION = int(monitor_section.find('option_chain_fetch_duration').text or self.OPTION_CHAIN_FETCH_DURATION)
                    
                    # Load health check interval (in seconds)
                    if monitor_section.find('health_check_interval') is not None:
                        self.HEALTH_CHECK_INTERVAL = int(monitor_section.find('health_check_interval').text or self.HEALTH_CHECK_INTERVAL)
                    
                    # Load symbols configuration
                    symbols_section = monitor_section.find('symbols')
                    if symbols_section is not None:
                        symbol_config = {}
                        for symbol_elem in symbols_section.findall('symbol'):
                            name = symbol_elem.get('name')
                            poll_seconds_text = symbol_elem.get('poll_seconds', '0,30')
                            poll_seconds = [int(s.strip()) for s in poll_seconds_text.split(',')]
                            strikes_text = symbol_elem.get('strikes')
                            strikes = int(strikes_text) if strikes_text else self.DEFAULT_STRIKES
                            symbol_config[name] = {"poll_seconds": poll_seconds, "strikes": strikes}
                        if symbol_config:
                            self.DEFAULT_SYMBOL_CONFIG = symbol_config
                
                # Load logging settings from general settings section
                settings_section = root.find('settings')
                if settings_section is not None:
                    if settings_section.find('log_level') is not None:
                        log_level_text = settings_section.find('log_level').text or 'INFO'
                        self.LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)
                
                # Load cutoff time settings
                if monitor_section is not None:
                    if monitor_section.find('cutoff_enabled') is not None:
                        self.CUTOFF_ENABLED = monitor_section.find('cutoff_enabled').text.lower() == 'true'
                    if monitor_section.find('cutoff_hour') is not None:
                        self.CUTOFF_HOUR = int(monitor_section.find('cutoff_hour').text or self.CUTOFF_HOUR)
                    if monitor_section.find('cutoff_minute') is not None:
                        self.CUTOFF_MINUTE = int(monitor_section.find('cutoff_minute').text or self.CUTOFF_MINUTE)
                
                # Load historical data settings
                historical_section = root.find('historical_data')
                if historical_section is not None:
                    if historical_section.find('enabled') is not None:
                        self.HISTORICAL_DATA_ENABLED = historical_section.find('enabled').text.lower() == 'true'
                    if historical_section.find('backdays') is not None:
                        self.HISTORICAL_BACKDAYS = int(historical_section.find('backdays').text or self.HISTORICAL_BACKDAYS)
                    if historical_section.find('duration') is not None:
                        self.HISTORICAL_DURATION = int(historical_section.find('duration').text or self.HISTORICAL_DURATION)
                    if historical_section.find('csv_export_enabled') is not None:
                        self.HISTORICAL_CSV_EXPORT_ENABLED = historical_section.find('csv_export_enabled').text.lower() == 'true'
                    
                    # Load historical symbols configuration
                    symbols_section = historical_section.find('symbols')
                    if symbols_section is not None:
                        historical_symbols = []
                        for symbol_elem in symbols_section.findall('symbol'):
                            name = symbol_elem.get('name')
                            if name:
                                historical_symbols.append(name)
                        if historical_symbols:
                            self.HISTORICAL_SYMBOLS = historical_symbols
                
                # Load live data settings
                live_section = root.find('live_data')
                if live_section is not None:
                    if live_section.find('enabled') is not None:
                        self.LIVE_DATA_ENABLED = live_section.find('enabled').text.lower() == 'true'
                    if live_section.find('csv_export_enabled') is not None:
                        self.LIVE_DATA_CSV_EXPORT_ENABLED = live_section.find('csv_export_enabled').text.lower() == 'true'
                    
                    # Load live data symbols configuration
                    symbols_section = live_section.find('symbols')
                    if symbols_section is not None:
                        live_symbols = []
                        for symbol_elem in symbols_section.findall('symbol'):
                            name = symbol_elem.get('name')
                            if name:
                                live_symbols.append(name)
                        if live_symbols:
                            self.LIVE_DATA_SYMBOLS = live_symbols
                
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}. Using defaults.")
        else:
            logger.info(f"Config file {self.config_file} not found. Using defaults.")
        
        # Environment variables override XML config
        if os.getenv('DEFAULT_STRIKES'):
            self.DEFAULT_STRIKES = int(os.getenv('DEFAULT_STRIKES'))
        if os.getenv('API_HOST'):
            self.API_HOST = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            self.API_PORT = int(os.getenv('API_PORT'))
        if os.getenv('AUTO_START'):
            self.AUTO_START = os.getenv('AUTO_START').lower() == 'true'
        if os.getenv('MAX_SYMBOLS'):
            self.MAX_SYMBOLS = int(os.getenv('MAX_SYMBOLS'))
        if os.getenv('LOG_LEVEL'):
            self.LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL').upper(), logging.INFO)
        if os.getenv('OPTION_MONITOR_ENABLED'):
            self.OPTION_MONITOR_ENABLED = os.getenv('OPTION_MONITOR_ENABLED').lower() == 'true'
        if os.getenv('CUTOFF_ENABLED'):
            self.CUTOFF_ENABLED = os.getenv('CUTOFF_ENABLED').lower() == 'true'
        if os.getenv('CUTOFF_HOUR'):
            self.CUTOFF_HOUR = int(os.getenv('CUTOFF_HOUR'))
        if os.getenv('CUTOFF_MINUTE'):
            self.CUTOFF_MINUTE = int(os.getenv('CUTOFF_MINUTE'))
        if os.getenv('HEALTH_CHECK_INTERVAL'):
            self.HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL'))
        if os.getenv('HISTORICAL_DATA_ENABLED'):
            self.HISTORICAL_DATA_ENABLED = os.getenv('HISTORICAL_DATA_ENABLED').lower() == 'true'
        if os.getenv('HISTORICAL_BACKDAYS'):
            self.HISTORICAL_BACKDAYS = int(os.getenv('HISTORICAL_BACKDAYS'))
        if os.getenv('HISTORICAL_DURATION'):
            self.HISTORICAL_DURATION = int(os.getenv('HISTORICAL_DURATION'))
        if os.getenv('HISTORICAL_CSV_EXPORT_ENABLED'):
            self.HISTORICAL_CSV_EXPORT_ENABLED = os.getenv('HISTORICAL_CSV_EXPORT_ENABLED').lower() == 'true'
        if os.getenv('HISTORICAL_SYMBOLS'):
            # Comma-separated list of symbols
            self.HISTORICAL_SYMBOLS = [s.strip() for s in os.getenv('HISTORICAL_SYMBOLS').split(',')]
        if os.getenv('LIVE_DATA_ENABLED'):
            self.LIVE_DATA_ENABLED = os.getenv('LIVE_DATA_ENABLED').lower() == 'true'
        if os.getenv('LIVE_DATA_CSV_EXPORT_ENABLED'):
            self.LIVE_DATA_CSV_EXPORT_ENABLED = os.getenv('LIVE_DATA_CSV_EXPORT_ENABLED').lower() == 'true'
        if os.getenv('LIVE_DATA_SYMBOLS'):
            # Comma-separated list of symbols
            self.LIVE_DATA_SYMBOLS = [s.strip() for s in os.getenv('LIVE_DATA_SYMBOLS').split(',')]

    def get_default_symbol_config(self) -> Dict[str, Dict[str, Any]]:
        """Get default symbol configuration."""
        return self.DEFAULT_SYMBOL_CONFIG.copy()

    def get_api_settings(self) -> Dict[str, Any]:
        """Get API-related settings."""
        return {
            'host': self.API_HOST,
            'port': self.API_PORT,
            'auto_start': self.AUTO_START
        }

    def get_logging_settings(self) -> Dict[str, Any]:
        """Get logging-related settings."""
        return {
            'level': self.LOG_LEVEL,
            'format': self.LOG_FORMAT,
            'date_format': self.LOG_DATE_FORMAT,
            'max_bytes': self.LOG_MAX_BYTES,
            'backup_count': self.LOG_BACKUP_COUNT
        }

    def get_monitor_defaults(self) -> Dict[str, Any]:
        """Get default settings for monitor."""
        return {
            'symbol_config': self.get_default_symbol_config(),
            'default_strikes': self.DEFAULT_STRIKES
        }

    def validate_symbol_config(self, symbol_config: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate symbol configuration format."""
        if not isinstance(symbol_config, dict):
            return False, "Symbol config must be a dictionary"
        
        if len(symbol_config) > self.MAX_SYMBOLS:
            return False, f"Cannot monitor more than {self.MAX_SYMBOLS} symbols"

        for symbol, config in symbol_config.items():
            if not isinstance(symbol, str) or not symbol.strip():
                return False, f"Symbol must be a non-empty string"
            if not isinstance(config, dict):
                return False, f"Config for {symbol} must be a dictionary"
            if 'poll_seconds' not in config:
                return False, f"Config for {symbol} must include 'poll_seconds'"
            if 'strikes' not in config:
                return False, f"Config for {symbol} must include 'strikes'"
            
            poll_secs = config['poll_seconds']
            strikes = config['strikes']
            
            if not isinstance(poll_secs, list) or len(poll_secs) == 0:
                return False, f"Poll seconds for {symbol} must be a non-empty list"
            if not all(isinstance(sec, int) and 0 <= sec <= 59 for sec in poll_secs):
                return False, f"Poll seconds for {symbol} must be integers 0-59"
            if not isinstance(strikes, int) or strikes < 1 or strikes > 50:
                return False, f"Strikes for {symbol} must be between 1 and 50"
            # Check minimum interval between polls
            if len(poll_secs) > 1:
                sorted_secs = sorted(poll_secs)
                for i in range(len(sorted_secs) - 1):
                    if sorted_secs[i+1] - sorted_secs[i] < self.MIN_POLL_INTERVAL:
                        return False, f"Minimum {self.MIN_POLL_INTERVAL}s interval required between polls for {symbol}"

        return True, "Valid"

    def get_log_file_path(self, name: str = "") -> str:
        """Get log file path."""
        # Create logs folder if it doesn't exist
        logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        if name:
            return os.path.join(logs_dir, f'{name}.log')
        else:
            return os.path.join(logs_dir, 'app.log')