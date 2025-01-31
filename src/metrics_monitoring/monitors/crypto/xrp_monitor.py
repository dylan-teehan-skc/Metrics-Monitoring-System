from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from datetime import datetime

class XRPMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the XRP Monitor"""
        super().__init__()
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol=XRPEUR"
        self.enabled = self.config['monitoring']['xrp']['enabled']
    
    def get_name(self) -> str:
        return "XRP"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("XRP monitoring is disabled in config")
            return {}

        try:
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
            self.logger.error(f"Error fetching XRP price: {str(e)}")
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
            self.logger.info(f"XRP Price: €{metrics['price_eur']:.4f} {metrics['currency']}")
