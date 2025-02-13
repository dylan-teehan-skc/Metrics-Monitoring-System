from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class HumidityMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the Humidity Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['Weather']['humidity']['enabled']
        self.api_url = self.config['monitoring']['Weather']['humidity']['api_url']
    
    def get_name(self) -> str:
        return "humidity"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("Humidity monitoring is disabled in config")
            return {}

        try:
            with BlockTimer('Collect Humidity metrics'):
                response = requests.get(self.api_url)
                response.raise_for_status()
                data = response.json()
                
            if 'current' in data and 'humidity' in data['current']:
                humidity = float(data['current']['humidity'])
                return {
                    'value': humidity,
                    'unit': 'Percent'
                }
            else:
                self.logger.error("Humidity data not found in response")
                return {
                    'value': None,
                    'unit': 'Percent',
                    'error': 'Humidity data not found'
                }
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching humidity data: {str(e)}")
            return {
                'value': None,
                'unit': 'Percent',
                'error': str(e)
            }
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        if not self.enabled or not metrics:
            return
        if metrics.get('error') is None and metrics.get('value') is not None:
            self.logger.info(f"Humidity: {metrics['value']:.2f} {metrics['unit']}") 