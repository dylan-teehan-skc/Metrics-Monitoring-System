from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class MemoryMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the MemoryMonitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['System']['memory_usage']['enabled']
    
    def get_name(self) -> str:
        return "memory_usage"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("Memory monitoring is disabled in config")
            return {}

        try:
            with BlockTimer("Collect Memory metrics"):
                return {
                    'value': psutil.virtual_memory().percent,
                    'unit': 'percent'
                }
        except Exception as e:
            self.logger.error(f"Error collecting Memory metrics: {str(e)}")
            return {}

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected Memory metrics"""
        if metrics:
            self.logger.info(f"Memory Usage: {metrics['value']}%") 