import logging
from .colored_formatter import ColoredFormatter
import os

def setup_logger(config: dict) -> logging.Logger:
    """Set up and configure the logger based on config"""
    log_config = config['logging']
    log_targets = log_config['targets']
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = []  # Clear any existing handlers
    
    # File Logger
    if log_targets['file']['enabled']:
        # Create logs directory if it doesn't exist
        log_path = log_targets['file']['path']
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        _add_file_handler(root_logger, log_targets['file'])
    
    # Console Logger
    if log_targets['console']['enabled']:
        _add_console_handler(root_logger, log_targets['console'])
    
    # Default Handler
    if not root_logger.handlers:
        _add_default_handler(root_logger)
    
    return root_logger

def _add_file_handler(logger: logging.Logger, file_config: dict):
    """Add file handler to logger"""
    file_handler = logging.FileHandler(file_config['path'])
    file_handler.setLevel(file_config['level'])
    file_handler.setFormatter(logging.Formatter(file_config['format']))
    logger.addHandler(file_handler)

def _add_console_handler(logger: logging.Logger, console_config: dict):
    """Add console handler to logger"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_config['level'])
    
    if console_config.get('use_colors', True):
        formatter = ColoredFormatter(
            console_config['format'],
            console_config.get('colors', {})
        )
    else:
        formatter = logging.Formatter(console_config['format'])
        
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def _add_default_handler(logger: logging.Logger):
    """Add default console handler if no handlers are configured"""
    default_handler = logging.StreamHandler()
    default_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(default_handler)
    logger.warning("No logging targets enabled, using default console logger") 