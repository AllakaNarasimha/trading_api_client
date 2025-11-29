#!/usr/bin/env python3
"""
Option Chain Monitor - API Version

Simple REST API to control option chain monitoring.
Easy to understand and maintain.

Module Organization:
- client.utils.config: Configuration management
- client.utils.monitor: Option chain monitoring logic
- client.utils.api: Flask REST API
- client.utils.cutoff_timer: Scheduled shutdown capability
"""

import os
import signal
import ssl
import logging
from functools import wraps
from logging.handlers import RotatingFileHandler

import requests
from trading_api import FyersAPI, IPriceWatcher
import urllib3

from client.utils.config import Config
from client.utils.monitor import OptionChainMonitor
from client.utils.api import OptionChainAPI
from client.utils.cutoff_timer import CutoffTimer
from client.watchlist import PriceWatcher

# ============================================================================
# SSL Configuration
# ============================================================================

# Disable SSL verification (temporary fix for certificate issues)
ssl._create_default_https_context = ssl._create_unverified_context

# Also disable requests SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch requests to disable SSL verification
_original_request = requests.request
@wraps(_original_request)
def _patched_request(*args, **kwargs):
    kwargs.setdefault('verify', False)
    return _original_request(*args, **kwargs)
requests.request = _patched_request


# ============================================================================
# Global Configuration Instance
# ============================================================================

config = Config()


# ============================================================================
# Setup Logging
# ============================================================================

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = config.get_log_file_path(script_dir)
logging_settings = config.get_logging_settings()

# Setup root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging_settings['level'])

# Remove existing handlers to avoid duplicates
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

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
root_logger.addHandler(file_handler)

# Console handler
console = logging.StreamHandler()
console.setLevel(logging_settings['level'])
console_formatter = logging.Formatter(logging_settings['format'])
console.setFormatter(console_formatter)
root_logger.addHandler(console)

logger = logging.getLogger(__name__)


# ============================================================================
# Global Instances
# ============================================================================

# Create global instances
monitor = OptionChainMonitor()
api = OptionChainAPI(monitor)

def shutdown_handler(signum: int, frame) -> None:
    """Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    try:
        if monitor.monitor_running:
            monitor.stop_event.set()
            if monitor.monitor_thread:
                monitor.monitor_thread.join(timeout=10)
        monitor._cleanup_resources()
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
    finally:
        os._exit(0)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Start the API server and optionally auto-start monitoring."""

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("="*60)
    logger.info("Option Chain Monitor API - Starting")
    logger.info("="*60)
    logger.info(f"Log file: {log_file}")
    logger.info(f"API Host: {config.API_HOST}:{config.API_PORT}")
    logger.info(f"Max symbols: {config.MAX_SYMBOLS}")
    logger.info(f"Default strikes: {config.DEFAULT_STRIKES}")
    logger.info(f"Default symbol config:")
    for symbol, config_data in config.get_default_symbol_config().items():
        logger.info(f"  {symbol}: poll at seconds {config_data['poll_seconds']}, strikes: {config_data['strikes']}")
    logger.info(f"Auto-start enabled: {config.AUTO_START}")
    logger.info(f"Cutoff timer enabled: {config.CUTOFF_ENABLED}")
    if config.CUTOFF_ENABLED:
        logger.info(f"Cutoff time: {config.CUTOFF_HOUR:02d}:{config.CUTOFF_MINUTE:02d}")
    logger.info("="*60)

    # Initialize cutoff timer if enabled
    cutoff_timer = None
    if config.CUTOFF_ENABLED:
        logger.info(f"Initializing cutoff timer for {config.CUTOFF_HOUR:02d}:{config.CUTOFF_MINUTE:02d}")
        try:
            cutoff_timer = CutoffTimer(config.CUTOFF_HOUR, config.CUTOFF_MINUTE)
            cutoff_timer.start()
            logger.info("[OK] Cutoff timer started")
        except Exception as e:
            logger.error(f"[ERROR] Failed to start cutoff timer: {e}", exc_info=True)

    # Auto-start monitoring if enabled
    if config.AUTO_START:
        logger.info("Auto-starting monitor...")
        try:
            success, message = monitor.start_monitoring()
            if success:
                logger.info(f"[OK] {message}")
            else:
                logger.warning(f"[ERROR] Auto-start failed: {message}")
        except Exception as e:
            logger.error(f"[ERROR] Auto-start error: {e}", exc_info=True)

    logger.info("API endpoints available:")
    logger.info(f"  GET  http://localhost:{config.API_PORT}/api/health")
    logger.info(f"  GET  http://localhost:{config.API_PORT}/api/status")
    logger.info(f"  POST http://localhost:{config.API_PORT}/api/start")
    logger.info(f"  POST http://localhost:{config.API_PORT}/api/add-symbol")
    logger.info(f"  POST http://localhost:{config.API_PORT}/api/stop")
    logger.info("="*60)

    # Start Flask API server
    try:
        api.run(host=config.API_HOST, port=config.API_PORT, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}", exc_info=True)
        shutdown_handler(signal.SIGTERM, None)

def checkOnline():
    """Check if the API server is online."""
    try:
        priceWatcher: PriceWatcher  = FyersAPI()
        status = priceWatcher.get_market_status()
        logger.info(f"API server is online. Market status: {status}")
    except Exception as e:
        logger.error(f"Failed to connect to API server: {e}", exc_info=True)

if __name__ == "__main__":
    # main()
    checkOnline()
