"""System monitoring module"""
from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class SystemMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the SystemMonitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['system_metrics']['enabled']
        self.enabled_metrics = self.config['monitoring']['system_metrics']['metrics']
        self.logger.debug(f"System monitor initialized with metrics: {self.enabled_metrics}")
    
    def get_name(self) -> str:
        return "System"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("System monitoring is disabled in config")
            return {}

        try:
            with BlockTimer("Collect system metrics"):
                metrics = {}
                
                # Only collect configured metrics
                if 'cpu_usage' in self.enabled_metrics:
                    metrics['cpu'] = {
                        'value': psutil.cpu_percent(interval=self.update_interval),
                        'unit': 'percent'
                    }
                    
                if 'memory_usage' in self.enabled_metrics:
                    metrics['memory'] = {
                        'value': psutil.virtual_memory().percent,
                        'unit': 'percent'
                    }
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
        
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        if not self.enabled:
            return        
        if 'cpu' in metrics:
            self.logger.info(f"CPU Usage: {metrics['cpu']['value']}%")
        if 'memory' in metrics:
            self.logger.info(f"Memory Usage: {metrics['memory']['value']}%") 