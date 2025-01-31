import json
from typing import Dict, Any
from datetime import datetime
import os

class MetricsModel:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.template = self._load_template()
        
    def _load_template(self, template_name="metrics_template.json"):
        """Load the metrics template from JSON file"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            template_name
        )
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def create_metrics_structure(self, collected_metrics: Dict[str, Dict]) -> Dict:
        """Create metrics structure from template and current metrics"""
        timestamp = datetime.now()
        
        # Create a deep copy of the template
        metrics = json.loads(json.dumps(self.template))
        
        # Update metadata
        metrics['metadata']['source'] = self.app_name
        metrics['metadata']['timestamp']['iso'] = timestamp.isoformat()
        metrics['metadata']['timestamp']['unix'] = int(timestamp.timestamp())
        
        # Update metrics data (only include collected metrics)
        metrics['data'] = collected_metrics
        
        # Update status
        metrics['status']['collection_duration_ms'] = int(
            (datetime.now() - timestamp).total_seconds() * 1000
        )
        
        return metrics 