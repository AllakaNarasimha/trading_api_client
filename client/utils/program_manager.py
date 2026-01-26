"""
Generic program restart/restart manager.
Can be used by any Python module to restart itself or any other Python script.
"""

import subprocess
import sys
import time
import logging
import os
from typing import Optional

class ProgramManager:
    """Manages program restart and lifecycle."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize ProgramManager.
        
        Args:
            logger: Logger instance (optional, creates one if not provided)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def restart_program(self, script_path: Optional[str] = None, delay: int = 5, args: Optional[list] = None):
        """
        Restart the current program or specified script.
        
        Args:
            script_path: Path to script to restart. If None, uses sys.argv[0]
            delay: Seconds to wait before restart (default: 5)
            args: Additional arguments to pass to the script (list of strings)
        """
        self.logger.info("=" * 60)
        self.logger.info("CRITICAL ERROR - Restarting program...")
        self.logger.info("=" * 60)

        python_exe = sys.executable
        if script_path is None:
            script_path = sys.argv[0]
        script_path = os.path.abspath(script_path)

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Restart script not found: {script_path}")

        cmd_args = [python_exe, script_path]
        if args:
            cmd_args.extend(args)
        
        self.logger.info(f"arguments: {cmd_args},  Waiting {delay} seconds before restart...")
        time.sleep(delay)
        
        

        # proc = subprocess.Popen(cmd_args, creationflags=subprocess.DETACHED_PROCESS, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.getcwd())
        try:
            # Call the launch_python_program.bat
            self.restart_application(10)  
        except Exception as e:
            self.logger.error(f"Failed to restart program: {e}", exc_info=True)
            raise e          


    
    def start_live_data_fetcher(self):
        try:  
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.logger.info(f"Script directory: {script_dir}")
            
            # The bat file is located in the same directory as this script when installed
            bat_path = os.path.join(script_dir, 'launch_python_program.bat')

            if os.path.exists(bat_path):
                self.logger.info(f"Bat file exists at: {bat_path}")
                subprocess.run([bat_path])  
            else:
                self.logger.error(f"Bat file does not exist at: {bat_path}")

        except Exception as e:
            self.logger.error(f"Error in test_bat(): {e}", exc_info=True)
    
    def restart_application(self, delay: int = 5):
        """
        Restart the current Python application, regardless of
        which module calls this function.
        """
        self.logger.critical("Application restart requested")
        self.logger.info("Restarting in %s seconds...", delay)

        time.sleep(delay)

        python = sys.executable
        args = sys.argv[:]

        self.logger.info("sys.executable: %s", python)
        self.logger.info("sys.argv: %s", args)

        # Handle `python -m module` case
        # if len(args) >= 2 and args[0] == "-m":
        #     self.logger.info(f"Restarting using -m module argument {args[1]}")
        #     os.execv(python, [python, "-m", args[1]])
        # else:
        #     self.logger.info(f"Restarting using script path argument {args[0]}")
 
        cmd = os.environ.get("LIVE_FETCHER")
        if not cmd:
            self.logger.error("LIVE_FETCHER not set — cannot restart")
            return

        self.logger.info("Restarting using command: %s", cmd)

        subprocess.Popen(cmd, shell=True)
        os._exit(0)
    
    def restart_current_program(self, delay: int = 5):
        """
        Restart the currently running program (sys.argv[0]).
        
        Args:
            delay: Seconds to wait before restart (default: 5)
        """
        self.restart_program(script_path=None, delay=delay)
