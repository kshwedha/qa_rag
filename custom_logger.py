import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

class CustomLogger:
    """
    - Rotating file handler to prevent large log files
    - Customizable log levels and formats
    - Singleton pattern for consistent logger instance
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one logger instance exists"""
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, logger_name='app', log_level=logging.INFO, 
                 log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                 log_file='logs/app.log', max_file_size=10*1024*1024, backup_count=5):
        """
        Initialize the logger with customizable options
        
        Args:
            logger_name (str): Name of the logger
            log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO)
            log_format (str): Format string for log messages
            log_file (str): Path to the log file
            max_file_size (int): Maximum size of each log file in bytes before rotation
            backup_count (int): Number of backup log files to keep
        """
        if self._initialized:
            return
            
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
                
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=max_file_size, 
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.error(f"Failed to create file handler: {e}")
            
        self._initialized = True
        
    def get_logger(self):
        """Return the configured logger instance"""
        return self.logger

# Create a default logger instance for direct import
logger = CustomLogger().get_logger()

# Convenience methods that can be imported directly
def debug(message):
    logger.debug(message)
    
def info(message):
    logger.info(message)
    
def warning(message):
    logger.warning(message)
    
def error(message):
    logger.error(message)
    
def critical(message):
    logger.critical(message)
    
def exception(message):
    logger.exception(message)

# for performance tracking, can be implemented
def log_execution_time(func):
    """Decorator to log execution time of functions"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.4f}s")
        return result
    return wrapper