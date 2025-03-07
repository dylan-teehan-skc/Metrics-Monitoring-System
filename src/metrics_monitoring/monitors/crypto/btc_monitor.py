from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class BTCMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the BTC Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['Crypto']['btc']['enabled']
        self.api_url = self.config['monitoring']['Crypto']['btc']['api_url']
    
    def get_name(self) -> str:
        return "btc"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("BTC monitoring is disabled in config")
            return {}

        try:
            with BlockTimer('Collect BTC metrics'):
                response = requests.get(self.api_url)
                response.raise_for_status()
                data = response.json()
            
            if 'price' not in data:
                self.logger.error("Invalid response format: 'price' field not found")
                return {
                    'value': None,
                    'unit': 'EUR',
                    'error': 'Invalid response format: price field not found'
                }
            
            price = float(data['price'])
            return {
                'value': price,
                'unit': 'EUR'
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching BTC price: {str(e)}")
            return {
                'value': None,
                'unit': 'EUR',
                'error': str(e)
            }
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        if not self.enabled or not metrics:
            return
        if metrics.get('error') is None and metrics.get('value') is not None:
            self.logger.info(f"BTC Price: €{metrics['value']:.4f} {metrics['unit']}") 