from typing import Dict, Any
from abc import ABC, abstractmethod
from src.config.config_loader import load_config
from src.logging.logger_setup import setup_logger
import logging

class BaseMonitor(ABC):
    """Abstract base class for all monitors"""
    
    def __init__(self):
        """Initialize the base monitor"""
        self.config = load_config()
        self.logger = setup_logger(self.config)  # Use the configured root logger
        self._running = True
        self.update_interval = self.config['monitoring']['update_interval']
        self.logger.debug(f"{self.get_name()} Monitor Initialized")

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the monitor"""
        pass

    @abstractmethod
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        pass

    @abstractmethod
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        pass

    def stop(self):
        """Stop the monitor gracefully"""
        self.logger.debug(f"Stopping {self.get_name()} monitor...")
        self._running = False
        self.logger.debug(f"{self.get_name()} monitor stopped")

    def is_running(self) -> bool:
        """Check if the monitor is running"""
        return self._running 