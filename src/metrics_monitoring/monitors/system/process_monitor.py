from ..base_monitor import BaseMonitor
import psutil
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class ProcessMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the Process Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['System']['process_count']['enabled']
    
    def get_name(self) -> str:
        return "process_count"

    def collect_metrics(self) -> Dict[str, Any]:
        if not self.enabled:
            self.logger.warning("Process monitoring is disabled in config")
            return {}

        try:
            with BlockTimer("Collect Process metrics"):
                process_count = len(psutil.pids())
                return {
                    'value': process_count,
                    'unit': 'count'
                }
        except Exception as e:
            self.logger.error(f"Error collecting Process metrics: {str(e)}")
            return {}

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected Process metrics"""
        if metrics:
            self.logger.info(f"Number of Running Processes: {metrics['value']}") 