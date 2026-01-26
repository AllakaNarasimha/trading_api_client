"""Utility functions for file operations."""

import csv
import datetime
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class FileUtils:
    """Utility class for file and path operations."""
    
    @staticmethod
    def get_csv_file_path(symbol: str, data_type: str = 'LIVE') -> str:
        """
        Generate CSV file path for market data.
        
        Args:
            symbol: Stock symbol
            data_type: Type of data (e.g., 'LIVE', 'HISTORICAL')
            
        Returns:
            str: Full path to CSV file
        """
        current_datetime = datetime.datetime.now()
        folder_name = current_datetime.strftime('%b%Y').lower()  # e.g., 'dec2025'
        csv_data_dir = os.path.join(folder_name, 'csv_data')
        os.makedirs(csv_data_dir, exist_ok=True)
        
        # Create filename
        current_date = current_datetime.strftime('%d%m%y')
        year = current_datetime.year
        symbol_clean = symbol.replace(':', '_').replace('-', '_')
        filename = f"{current_date}_{year}_{symbol_clean}_{data_type}.csv"
        file_path = os.path.join(csv_data_dir, filename)
        
        return file_path
    
    @staticmethod
    def sanitize_symbol_name(symbol: str) -> str:
        """
        Sanitize symbol name for use in filenames and database names.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE:NIFTY50-INDEX')
            
        Returns:
            str: Sanitized symbol name (e.g., 'NSE_NIFTY50_INDEX')
        """
        return symbol.replace(':', '_').replace('-', '_')
    
    @staticmethod
    def get_symbol_name(symbol: str) -> str:
        """
        Extract symbol name from full symbol string.
        
        Args:
            symbol: Full symbol (e.g., 'NSE:NIFTY50-INDEX')
            
        Returns:
            str: Symbol name (e.g., 'NIFTY50-INDEX')
        """
        return symbol.split(':')[-1] if ':' in symbol else symbol
    
    @staticmethod
    def save_dict_list_to_csv(data: List[Dict[str, Any]], file_path: str, mode: str = 'w') -> bool:
        """
        Save a list of dictionaries to CSV file.
        
        Args:
            data: List of dictionaries to save
            file_path: Path to the CSV file
            mode: File mode ('w' for write/overwrite, 'a' for append)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning(f"No data to save to CSV: {file_path}")
                return False
            
            if not isinstance(data[0], dict):
                logger.error(f"Data is not in dict format for CSV export: {file_path}")
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            file_exists = os.path.exists(file_path)
            
            with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if new file or write mode
                if mode == 'w' or (mode == 'a' and not file_exists):
                    writer.writeheader()
                
                writer.writerows(data)
            
            logger.debug(f"Saved {len(data)} records to CSV: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save CSV {file_path}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def append_dict_to_csv(data: Dict[str, Any], file_path: str) -> bool:
        """
        Append a single dictionary record to CSV file.
        Creates file with header if it doesn't exist.
        
        Args:
            data: Dictionary to append
            file_path: Path to the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not data or not isinstance(data, dict):
                logger.warning(f"No data to append to CSV: {file_path}")
                return False
            
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            file_exists = os.path.exists(file_path)
            
            with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(data)
            
            logger.debug(f"Appended record to CSV: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append to CSV {file_path}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def get_csv_writer_and_file(file_path: str, fieldnames: List[str], 
                                 mode: str = 'a') -> tuple:
        """
        Get CSV writer and file handle for streaming writes.
        Useful for keeping file open across multiple writes.
        
        Args:
            file_path: Path to the CSV file
            fieldnames: List of field names for CSV header
            mode: File mode ('w' for write, 'a' for append)
            
        Returns:
            tuple: (csv_writer, file_handle) or (None, None) if error
        """
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            file_exists = os.path.exists(file_path)
            file_handle = open(file_path, mode, newline='', encoding='utf-8')
            writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
            
            # Write header if new file or write mode
            if mode == 'w' or (mode == 'a' and not file_exists):
                writer.writeheader()
            
            return writer, file_handle
            
        except Exception as e:
            logger.error(f"Failed to create CSV writer for {file_path}: {e}")
            return None, None


# Backward compatibility: module-level function
def get_csv_file_path(symbol: str, data_type: str = 'LIVE') -> str:
    """
    Generate CSV file path for market data.
    (Backward compatibility wrapper)
    
    Args:
        symbol: Stock symbol
        data_type: Type of data (e.g., 'LIVE', 'HISTORICAL')
        
    Returns:
        str: Full path to CSV file
    """
    return FileUtils.get_csv_file_path(symbol, data_type)
