from ..base_monitor import BaseMonitor
import requests
from typing import Dict, Any
from src.utils.block_timer import BlockTimer

class PeopleInSpaceMonitor(BaseMonitor):
    def __init__(self):
        """Initialize the People in Space Monitor"""
        super().__init__()
        self.enabled = self.config['monitoring']['Space']['people_in_space']['enabled']
        self.api_url = self.config['monitoring']['Space']['people_in_space']['api_url']
    
    def get_name(self) -> str:
        return "people_in_space"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics specific to this monitor"""
        if not self.enabled:
            self.logger.warning("People in Space monitoring is disabled in config")
            return {}

        try:
            with BlockTimer('Collect People in Space metrics'):
                response = requests.get(self.api_url)
                response.raise_for_status()
                data = response.json()
            
            # Try to get the number directly from the response
            if isinstance(data, int):
                number_of_people = data
            # If it's a dictionary, try to get the number from the 'number' field
            elif isinstance(data, dict):
                if 'number' in data:
                    number_of_people = int(data['number'])
                # Fall back to counting people in the array if present
                elif 'people' in data and isinstance(data['people'], list):
                    number_of_people = len(data['people'])
                else:
                    self.logger.error("Invalid response format: no valid people count found")
                    return {
                        'value': None,
                        'unit': 'people',
                        'error': 'Invalid response format: no valid people count found'
                    }
            else:
                self.logger.error("Invalid response format: unexpected response type")
                return {
                    'value': None,
                    'unit': 'people',
                    'error': 'Invalid response format: unexpected response type'
                }

            return {
                'value': number_of_people,
                'unit': 'people'
            }

        except requests.RequestException as e:
            self.logger.error(f"Error fetching People in Space data: {str(e)}")
            return {
                'value': None,
                'unit': 'people',
                'error': str(e)
            }
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log the collected metrics"""
        if not self.enabled or not metrics:
            return
        if metrics.get('error') is None:
            self.logger.info(f"Number of People in Space: {metrics['value']}") 