from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class DiskMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the Disk Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['System']['disk_usage']['enabled']
    
    def get_name(self) -> str:
        return "disk_usage"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("Disk monitoring is disabled in config")
            return {}

        try:
            with BlockTimer("Collect Disk metrics"):
                disk_usage = psutil.disk_usage('/').percent
                return {
                    'value': disk_usage,
                    'unit': 'percent'
                }
        except Exception as e:
            self.logger.error(f"Error collecting Disk metrics: {str(e)}")
            return {}

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected Disk metrics"""
        if metrics:
            self.logger.info(f"Disk Usage: {metrics['value']}%") 