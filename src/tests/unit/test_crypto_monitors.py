"""
Unit tests for cryptocurrency monitoring components.

This module contains unit tests for Bitcoin and other cryptocurrency monitors.
"""

import unittest
from unittest.mock import Mock, patch
import logging
import requests
from src.metrics_monitoring.monitors.crypto.btc_monitor import BTCMonitor

class TestCryptoMonitors(unittest.TestCase):
    """Test cases for cryptocurrency monitoring components"""
    
    def setUp(self):
        """Initialize monitors before each test"""
        self.btc_monitor = BTCMonitor()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.btc_monitor.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_monitor_initialization(self):
        """Test that BTC monitor is properly initialized"""
        self.assertIsNotNone(self.btc_monitor)
        self.assertEqual(self.btc_monitor.get_name(), "btc")
        self.assertTrue(hasattr(self.btc_monitor, 'api_url'))
    
    @patch('requests.get')
    def test_btc_metrics_collection_success(self, mock_get):
        """Test successful BTC price metrics collection"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'price': '45000.50'}
        mock_get.return_value = mock_response
        
        # Collect metrics
        metrics = self.btc_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 45000.50)
        self.assertEqual(metrics['unit'], 'EUR')
        self.assertNotIn('error', metrics)
    
    @patch('requests.get')
    def test_btc_metrics_collection_failure(self, mock_get):
        """Test BTC price metrics collection with API failure"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock to raise an exception
            mock_get.side_effect = requests.RequestException("API Error")
            
            # Collect metrics
            metrics = self.btc_monitor.collect_metrics()
            
            # Verify error handling
            self.assertIn('value', metrics)
            self.assertIn('unit', metrics)
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'EUR')
            self.assertEqual(metrics['error'], 'API Error')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_btc_invalid_response(self, mock_get):
        """Test handling of invalid API response format"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock with invalid response format
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'invalid_key': 'invalid_data'}
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.btc_monitor.collect_metrics()
            
            # Verify error handling for invalid response
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'EUR')
            self.assertIn('Invalid response format', metrics['error'])
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)

if __name__ == '__main__':
    unittest.main() 