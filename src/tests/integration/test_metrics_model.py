"""
Integration tests for metrics model.

This module tests the metrics model's interaction with collected data
and its integration with the monitoring system.
"""

import unittest
import logging
from src.metrics_monitoring.models.metrics_model import MetricsModel

class TestMetricsModel(unittest.TestCase):
    """Integration tests for MetricsModel"""
    
    def setUp(self):
        """Initialize model"""
        self.app_name = "test_app"
        self.metrics_model = MetricsModel(self.app_name)
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up resources"""
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_metrics_structure_creation(self):
        """Test creating metrics structure from collected data"""
        # Sample collected metrics
        collected_metrics = {
            "System": {
                "cpu_usage": {
                    "value": 45.5,
                    "unit": "percent"
                },
                "memory_usage": {
                    "value": 75.2,
                    "unit": "percent"
                }
            },
            "Crypto": {
                "btc": {
                    "value": 45000.50,
                    "unit": "EUR"
                }
            }
        }
        
        # Create metrics structure
        metrics = self.metrics_model.create_metrics_structure(collected_metrics)
        
        # Verify structure
        self.assertIsNotNone(metrics)
        self.assertIn('metadata', metrics)
        self.assertIn('data', metrics)
        self.assertEqual(metrics['metadata']['source'], self.app_name)
        self.assertIn('System', metrics['data'])
        self.assertIn('Crypto', metrics['data'])
    
    def test_error_handling(self):
        """Test handling of invalid metrics data"""
        # Invalid metrics data
        invalid_metrics = {
            "System": None,
            "Crypto": "invalid"
        }
        
        # Create metrics structure
        metrics = self.metrics_model.create_metrics_structure(invalid_metrics)
        
        # Verify empty result for invalid data
        self.assertEqual(metrics, {})
    
    def test_metrics_cleaning(self):
        """Test cleaning of metrics data"""
        # Metrics with error field
        metrics_with_error = {
            "System": {
                "cpu_usage": {
                    "value": 45.5,
                    "unit": "percent",
                    "error": None
                }
            }
        }
        
        # Create metrics structure
        metrics = self.metrics_model.create_metrics_structure(metrics_with_error)
        
        # Verify error field is None when present
        self.assertIn('data', metrics)
        self.assertIn('System', metrics['data'])
        self.assertIn('cpu_usage', metrics['data']['System'])
        self.assertEqual(metrics['data']['System']['cpu_usage']['error'], None)

if __name__ == '__main__':
    unittest.main() 