"""Metrics client for sending data to remote server"""
import json
import requests
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.timer import Timer
import time

class MetricsClient:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.retry_attempts = self.config['server']['retry_attempts']
        self.retry_delay = self.config['server']['retry_delay']
        
    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Serialize and send metrics to remote server"""
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                with Timer(self.server_url):
                    # Serialize metrics to JSON
                    json_data = json.dumps(metrics)
                    
                    # Send POST request to server
                    response = requests.post(
                        self.server_url,
                        data=json_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                
                return True
                
            except requests.RequestException as e:
                attempts += 1
                if attempts < self.retry_attempts:
                    self.logger.warning(f"Failed to send metrics (attempt {attempts}/{self.retry_attempts}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to send metrics after {self.retry_attempts} attempts: {str(e)}")
                    return False 