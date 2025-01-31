"""Simple timer utility for measuring execution time"""
import time
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config

logger = setup_logger(load_config())

class Timer:
    """Timer class that logs execution time of operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        duration = (end_time - self.start_time) * 1000  # Convert to milliseconds
        if exc_type:
            logger.error(f"Operation '{self.operation_name}' failed after {duration:.2f}ms: {str(exc_val)}")
        else:
            logger.info(f"Operation '{self.operation_name}' completed in {duration:.2f}ms") 