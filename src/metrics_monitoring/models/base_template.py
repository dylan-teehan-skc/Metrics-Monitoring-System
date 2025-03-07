from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import uuid

class BaseTemplate(ABC):
    @abstractmethod
    def create_structure(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create base metrics structure"""
        pass

class DefaultTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()
        self.mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                   for elements in range(0,8*6,8)][::-1])
        
    def create_structure(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create default metrics structure"""
        now = datetime.now()
        
        return {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'unix_timestamp': int(now.timestamp()),
            'metadata': {
                'source': 'Metrics Monitor',
                'system_id': self.mac_address,  # Using MAC address as system identifier
                'version': '1.0'
            },
            'data': metrics
        } 