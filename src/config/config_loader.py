import json
from typing import Dict
import os
from dotenv import load_dotenv

def load_config() -> Dict:
    try:
        load_dotenv()
        with open('config.json', 'r') as f:
            config = json.load(f)
            
            # Replace environment variables
            config['monitoring']['update_interval'] = int(os.getenv('METRICS_UPDATE_INTERVAL', 10))
            config['monitoring']['btc']['api_url'] = os.getenv('BINANCE_BTC_URL')
            config['monitoring']['xrp']['api_url'] = os.getenv('BINANCE_XRP_URL')
            config['server']['url'] = os.getenv('PYTHONAWAY_URL')
            
            return config
    except FileNotFoundError:
        raise Exception("Config file not found!")