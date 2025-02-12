from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

class BaseTemplate(ABC):
    @abstractmethod
    def create_structure(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create base metrics structure"""
        pass

class DefaultTemplate(BaseTemplate):
    def create_structure(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create default metrics structure"""
        now = datetime.now()
        
        return {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'unix_timestamp': int(now.timestamp()),
            'metadata': {
                'source': 'Metrics Monitor',
                'version': '1.0'
            },
            'data': metrics
        } 