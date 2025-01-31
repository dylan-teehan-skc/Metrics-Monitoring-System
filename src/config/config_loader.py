import json
from typing import Dict

def load_config() -> Dict:
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception("Config file not found!")