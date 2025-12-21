"""
Option Chain API - Flask REST API for monitoring control.
Provides endpoints to start, stop, and manage option chain monitoring.
"""

import datetime
import logging
from typing import Optional

from flask import Flask, jsonify, request

from client.utils.config import Config
from client.utils.option_chain_monitor import OptionChainMonitor

logger = logging.getLogger(__name__)
config = Config()


class OptionChainAPI:
    """Flask API class for option chain monitoring control."""

    def __init__(self, monitor: OptionChainMonitor):
        """Initialize API with monitor instance.

        Args:
            monitor: OptionChainMonitor instance
        """
        self.monitor = monitor
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        self.app.config['JSON_AS_ASCII'] = False
        # Disable Flask default logging to avoid duplicate logs
        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.WARNING)
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        self.app.add_url_rule('/api/health', 'health_check', self.health_check, methods=['GET'])
        self.app.add_url_rule('/api/start', 'start_monitor', self.start_monitor, methods=['POST'])
        self.app.add_url_rule('/api/add-symbol', 'add_symbol', self.add_symbol, methods=['POST'])
        self.app.add_url_rule('/api/stop', 'stop_monitor', self.stop_monitor, methods=['POST'])
        self.app.add_url_rule('/api/status', 'get_status', self.get_status, methods=['GET'])
        
        # Error handlers
        self.app.register_error_handler(404, self._handle_404)
        self.app.register_error_handler(500, self._handle_500)
    
    def _handle_404(self, error):
        """Handle 404 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'available_endpoints': ['/api/health', '/api/start', '/api/add-symbol', '/api/stop', '/api/status']
        }), 404
    
    def _handle_500(self, error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
    def health_check(self):
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'monitor_running': self.monitor.monitor_running
        }), 200

    def start_monitor(self):
        """Start the monitor with optional config.

        Request body (new format):
        {
            "symbol_config": {
                "NSE:NIFTY50-INDEX": {"poll_seconds": [0, 30], "strikes": 15},
                "NSE:NIFTYBANK-INDEX": {"poll_seconds": [0, 30], "strikes": 10}
            }
        }

        Request body (old format for backward compatibility):
        {
            "symbol_config": {"NSE:NIFTY50-INDEX": [0, 30], "NSE:NIFTYBANK-INDEX": [0, 30]},
            "number_of_strikes": 15
        }
        """
        try:
            data = request.get_json(silent=True) or {}
            symbol_config = data.get('symbol_config')
            default_strikes = data.get('number_of_strikes')
            
            # Validate default_strikes if provided
            if default_strikes is not None:
                if not isinstance(default_strikes, int):
                    return jsonify({
                        'status': 'error',
                        'message': 'number_of_strikes must be an integer'
                    }), 400

            success, message = self.monitor.start_monitoring(symbol_config, default_strikes)

            if success:
                return jsonify({
                    'status': 'success',
                    'message': message,
                    'symbol_config': self.monitor.current_symbols
                }), 200
            else:
                return jsonify({'status': 'error', 'message': message}), 400

        except Exception as e:
            logger.error(f"Start API error: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def add_symbol(self):
        """Add a new symbol to monitoring while running.

        Request body:
        {
            "symbol": "NSE:FINNIFTY-INDEX",
            "poll_seconds": [0, 30],  // Optional, defaults to [0, 30]
            "strikes": 15  // Optional, defaults to default_strikes
        }
        """
        try:
            data = request.get_json(silent=True) or {}
            new_symbol = data.get('symbol')
            poll_secs = data.get('poll_seconds')
            strikes = data.get('strikes')
            
            # Validate required field
            if not new_symbol:
                return jsonify({
                    'status': 'error',
                    'message': 'symbol field is required'
                }), 400
            
            # Validate poll_seconds if provided
            if poll_secs is not None and not isinstance(poll_secs, list):
                return jsonify({
                    'status': 'error',
                    'message': 'poll_seconds must be a list of integers'
                }), 400
            
            # Validate strikes if provided
            if strikes is not None and not isinstance(strikes, int):
                return jsonify({
                    'status': 'error',
                    'message': 'strikes must be an integer'
                }), 400

            success, message, symbol_config = self.monitor.add_symbol(new_symbol, poll_secs, strikes)

            if success:
                return jsonify({
                    'status': 'success',
                    'message': message,
                    'symbol_config': symbol_config
                }), 200
            else:
                return jsonify({'status': 'error', 'message': message}), 400

        except Exception as e:
            logger.error(f"Add symbol API error: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def stop_monitor(self):
        """Stop the monitor."""
        try:
            success, message = self.monitor.stop_monitoring()

            if success:
                return jsonify({
                    'status': 'success',
                    'message': message
                }), 200
            else:
                return jsonify({'status': 'error', 'message': message}), 400

        except Exception as e:
            logger.error(f"Stop API error: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def get_status(self):
        """Get current monitor status."""
        try:
            status = self.monitor.get_status()
            return jsonify({
                'status': 'success',
                'data': status
            }), 200

        except Exception as e:
            logger.error(f"Status API error: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def run(self, host: Optional[str] = None, port: Optional[int] = None, **kwargs) -> None:
        """Run the Flask application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional arguments passed to Flask.run()
        """
        host = host or config.API_HOST
        port = port or config.API_PORT
        logger.info(f"Starting Flask server on {host}:{port}")
        self.app.run(host=host, port=port, **kwargs)
