"""Metrics model for structuring monitoring data"""
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from .base_template import DefaultTemplate

class MetricsModel:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.template = DefaultTemplate()
        
    def create_metrics_structure(self, collected_metrics: Dict[str, Dict]) -> Dict:
        """Create metrics structure using template"""
        try:
            # Clean up metrics data
            cleaned_metrics = {}
            for monitor_name, monitor_data in collected_metrics.items():
                # Create a copy of the monitor data
                cleaned_data = dict(monitor_data)
                
                # Remove error field if it's None
                if 'error' in cleaned_data and cleaned_data['error'] is None:
                    del cleaned_data['error']
                    
                cleaned_metrics[monitor_name] = cleaned_data
            
            # Create structure using template
            metrics = self.template.create_structure(
                cleaned_metrics
            )
            
            # Override source with app name
            metrics['metadata']['source'] = self.app_name
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error creating metrics structure: {str(e)}")
            return {} 