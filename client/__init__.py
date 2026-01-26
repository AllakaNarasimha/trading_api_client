"""
Client package for trading_api demonstration and usage.
"""

# ============================================================================
# SSL Configuration - Applied when client package is imported
# ============================================================================
# Import ssl_config first to apply global SSL patches
from . import ssl_config  # noqa: F401

# ============================================================================

__version__ = "1.0.0"
__all__ = ["portfolio", "orders", "watchlist"]
