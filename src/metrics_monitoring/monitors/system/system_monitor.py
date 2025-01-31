"""System monitoring module"""
from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any

class SystemMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the SystemMonitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['system_metrics']['enabled']
    
    def get_name(self) -> str:
        return "System"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("System monitoring is disabled in config")
            return {}

        metrics = {
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=self.update_interval)
            },
            'memory': {
                'usage_percent': psutil.virtual_memory().percent
            }
        }
        return metrics
        
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.logger.info(f"CPU Usage: {metrics['cpu']['usage_percent']}%")
        self.logger.info(f"Memory Usage: {metrics['memory']['usage_percent']}%") 