"""Bitcoin price monitoring module"""
from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from datetime import datetime
from src.utils.timer import Timer

class BTCMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the BTC Monitor"""
        super().__init__()
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR"
        self.enabled = self.config['monitoring']['btc']['enabled']
    
    def get_name(self) -> str:
        return "BTC"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("BTC monitoring is disabled in config")
            return {}

        try:
            with Timer(self.api_url):
                response = requests.get(self.api_url)
                response.raise_for_status()
                data = response.json()
            
            price = float(data['price'])
            return {
                'price_eur': price,
                'currency': 'EUR',
                'last_update': datetime.now().isoformat(),
                'error': None
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching BTC price: {str(e)}")
            return {
                'price_eur': None,
                'currency': 'EUR',
                'last_update': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        if not self.enabled or not metrics:
            return
        if metrics.get('error') is None and metrics.get('price_eur') is not None:
            self.logger.info(f"BTC Price: €{metrics['price_eur']:.4f} {metrics['currency']}") 