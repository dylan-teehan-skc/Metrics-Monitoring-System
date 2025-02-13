from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class TemperatureMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the Temperature Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['Weather']['temperature']['enabled']
        self.api_url = self.config['monitoring']['Weather']['temperature']['api_url']
    
    def get_name(self) -> str:
        return "temperature"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("Temperature monitoring is disabled in config")
            return {}

        try:
            with BlockTimer('Collect Temperature metrics'):
                response = requests.get(self.api_url)
                response.raise_for_status()
                data = response.json()

            if 'current' in data and 'temp_c' in data['current']:
                temperature = float(data['current']['temp_c'])
                return {
                    'value': temperature,
                    'unit': 'Celsius'
                }
            else:
                self.logger.error("Temperature data not found in response")
                return {
                    'value': None,
                    'unit': 'Celsius',
                    'error': 'Temperature data not found'
                }
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching temperature data: {str(e)}")
            return {
                'value': None,
                'unit': 'Celsius',
                'error': str(e)
            }
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        if not self.enabled or not metrics:
            return
        if metrics.get('error') is None and metrics.get('value') is not None:
            self.logger.info(f"Temperature: {metrics['value']:.2f} {metrics['unit']}") 