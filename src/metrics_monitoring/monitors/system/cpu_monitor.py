from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class CPUMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the CPUMonitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['System']['cpu_usage']['enabled']
    
    def get_name(self) -> str:
        return "cpu_usage"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("CPU monitoring is disabled in config")
            return {}

        try:
            with BlockTimer("Collect CPU metrics"):
                return {
                    'value': psutil.cpu_percent(interval=self.update_interval),
                    'unit': 'percent'
                }
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {str(e)}")
            return {}

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected CPU metrics"""
        if metrics:
            self.logger.info(f"CPU Usage: {metrics['value']}%") 