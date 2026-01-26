#!/usr/bin/env python3
"""
Main entry point for the client package.
Runs the Option Chain Monitor API.
"""

from shlex import shlex
import sys
import os

# Ensure the parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from client.live_data_fetch_controller import LiveDataFetchController

os.environ["LIVE_FETCHER"] = shlex.join(
    [sys.executable] + sys.argv
)

if __name__ == "__main__":
    app = LiveDataFetchController()
    app.run()