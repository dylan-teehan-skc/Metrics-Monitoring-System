"""
Unit tests for space monitoring components.

This module contains unit tests for space-related monitors.
"""

import unittest
from unittest.mock import Mock, patch
import logging
import requests
from src.metrics_monitoring.monitors.space.people_in_space_monitor import PeopleInSpaceMonitor

class TestSpaceMonitors(unittest.TestCase):
    """Test cases for space monitoring components"""
    
    def setUp(self):
        """Initialize monitors before each test"""
        self.people_monitor = PeopleInSpaceMonitor()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.people_monitor.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_monitor_initialization(self):
        """Test that space monitor is properly initialized"""
        self.assertIsNotNone(self.people_monitor)
        self.assertEqual(self.people_monitor.get_name(), "people_in_space")
        self.assertTrue(hasattr(self.people_monitor, 'api_url'))
    
    @patch('requests.get')
    def test_people_metrics_collection_success_array(self, mock_get):
        """Test successful people in space metrics collection with people array"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'people': [
                {'name': 'John Doe', 'craft': 'ISS'},
                {'name': 'Jane Smith', 'craft': 'ISS'}
            ]
        }
        mock_get.return_value = mock_response
        
        # Collect metrics
        metrics = self.people_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 2)
        self.assertEqual(metrics['unit'], 'people')
        self.assertNotIn('error', metrics)
    
    @patch('requests.get')
    def test_people_metrics_collection_success_direct(self, mock_get):
        """Test successful people in space metrics collection with direct number"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = 12
        mock_get.return_value = mock_response
        
        # Collect metrics
        metrics = self.people_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 12)
        self.assertEqual(metrics['unit'], 'people')
        self.assertNotIn('error', metrics)
    
    @patch('requests.get')
    def test_people_metrics_collection_success_number_field(self, mock_get):
        """Test successful people in space metrics collection with number field"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'number': '12'}
        mock_get.return_value = mock_response
        
        # Collect metrics
        metrics = self.people_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 12)
        self.assertEqual(metrics['unit'], 'people')
        self.assertNotIn('error', metrics)
    
    @patch('requests.get')
    def test_people_metrics_collection_failure(self, mock_get):
        """Test people in space metrics collection with API failure"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock to raise an exception
            mock_get.side_effect = requests.RequestException("API Error")
            
            # Collect metrics
            metrics = self.people_monitor.collect_metrics()
            
            # Verify error handling
            self.assertIn('value', metrics)
            self.assertIn('unit', metrics)
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'people')
            self.assertEqual(metrics['error'], 'API Error')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_people_invalid_response(self, mock_get):
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
            metrics = self.people_monitor.collect_metrics()
            
            # Verify error handling for invalid response
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'people')
            self.assertEqual(metrics['error'], 'Invalid response format: no valid people count found')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)
    
    @patch('requests.get')
    def test_people_unexpected_response_type(self, mock_get):
        """Test handling of unexpected response type"""
        # Temporarily increase log level to suppress expected error messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock with unexpected response type
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = ["unexpected", "array", "type"]
            mock_get.return_value = mock_response
            
            # Collect metrics
            metrics = self.people_monitor.collect_metrics()
            
            # Verify error handling for invalid response
            self.assertIn('error', metrics)
            self.assertIsNone(metrics['value'])
            self.assertEqual(metrics['unit'], 'people')
            self.assertEqual(metrics['error'], 'Invalid response format: unexpected response type')
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)

if __name__ == '__main__':
    unittest.main() 