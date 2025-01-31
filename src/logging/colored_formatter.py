"""Custom colored formatter for console logging"""
import logging
from colorama import init, Fore, Style

init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter class to add colors to console output"""
    
    def __init__(self, format_str: str, colors: dict):
        super().__init__(format_str)
        self.colors = colors
        
        self.color_map = {
            'RED': Fore.RED,
            'GREEN': Fore.GREEN,
            'YELLOW': Fore.YELLOW,
            'BLUE': Fore.BLUE,
            'MAGENTA': Fore.MAGENTA,
            'CYAN': Fore.CYAN,
            'WHITE': Fore.WHITE
        }
    
    def format(self, record):
        formatted_msg = super().format(record)
        
        if record.levelname in self.colors:
            color = self.color_map.get(self.colors[record.levelname], '')
            return f"{color}{formatted_msg}{Style.RESET_ALL}"
        
        return formatted_msg 