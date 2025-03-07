"""
Unit tests for weather monitoring components.

This module contains unit tests for temperature and humidity monitors.
"""

import unittest
from unittest.mock import Mock, patch
import logging
from src.metrics_monitoring.monitors.weather.temperature_monitor import TemperatureMonitor
from src.metrics_monitoring.monitors.weather.humidity_monitor import HumidityMonitor

class TestWeatherMonitors(unittest.TestCase):
    """Test cases for weather monitoring components"""
    
    def setUp(self):
        """Initialize monitors before each test"""
        self.temp_monitor = TemperatureMonitor()
        self.humidity_monitor = HumidityMonitor()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.temp_monitor.stop()
        self.humidity_monitor.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_monitor_initialization(self):
        """Test weather monitors are properly initialized"""
        self.assertIsNotNone(self.temp_monitor)
        self.assertIsNotNone(self.humidity_monitor)
        self.assertEqual(self.temp_monitor.get_name(), "temperature")
        self.assertEqual(self.humidity_monitor.get_name(), "humidity")
    
    @patch('requests.get')
    def test_temperature_collection(self, mock_get):
        """Test temperature metrics collection"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'current': {'temp_c': 20.5}}
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.temp_monitor.collect_metrics()
            
            # Verify metrics format and values
            self.assertIn('value', metrics)
            self.assertIn('unit', metrics)
            self.assertEqual(metrics['value'], 20.5)
            self.assertEqual(metrics['unit'], 'Celsius')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_humidity_collection(self, mock_get):
        """Test humidity metrics collection"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'current': {'humidity': 65}}
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.humidity_monitor.collect_metrics()
            
            # Verify metrics format and values
            self.assertIn('value', metrics)
            self.assertIn('unit', metrics)
            self.assertEqual(metrics['value'], 65)
            self.assertEqual(metrics['unit'], 'Percent')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_temperature_invalid_response(self, mock_get):
        """Test handling of invalid temperature response format"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock with invalid response format
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'invalid_key': 'invalid_data'}
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.temp_monitor.collect_metrics()
            
            # Verify error handling for invalid response
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'Celsius')
            self.assertEqual(metrics['error'], 'Temperature data not found')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_humidity_invalid_response(self, mock_get):
        """Test handling of invalid humidity response format"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock with invalid response format
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'invalid_key': 'invalid_data'}
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.humidity_monitor.collect_metrics()
            
            # Verify error handling for invalid response
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'Percent')
            self.assertEqual(metrics['error'], 'Humidity data not found')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)

if __name__ == '__main__':
    unittest.main() 