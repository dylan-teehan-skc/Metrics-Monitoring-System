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
            config['monitoring']['Crypto']['btc']['api_url'] = os.getenv('BINANCE_BTC_URL')
            config['monitoring']['Crypto']['xrp']['api_url'] = os.getenv('BINANCE_XRP_URL')
            config['monitoring']['Weather']['temperature']['api_url'] = os.getenv('WEATHER_API_TEMPERATURE_URL')
            config['monitoring']['Weather']['humidity']['api_url'] = os.getenv('WEATHER_API_HUMIDITY_URL')
            config['server']['url'] = os.getenv('PYTHONAWAY_URL')
            return config
    except FileNotFoundError:
        raise Exception("Config file not found!")