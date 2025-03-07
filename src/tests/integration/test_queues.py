"""
Integration tests for queueing components.

This module contains integration tests for the queueing mechanisms.
These tests verify the actual functionality of the queues including
their interaction with the metrics processing system.
"""

import unittest
from unittest.mock import Mock, patch
import json
import time
import logging
from src.client.simple_queue import SimpleQueue
from src.client.priority_queue import PriorityMetricsQueue

class TestSimpleQueue(unittest.TestCase):
    """Integration tests for SimpleQueue implementation"""
    
    def setUp(self):
        """Initialize queue before each test"""
        self.queue = SimpleQueue()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.queue.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        # Restore original logging level
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_queue_initialization(self):
        """Test queue is properly initialized"""
        self.assertIsNotNone(self.queue)
        self.assertEqual(len(self.queue.queue), 0)
    
    def test_send_metrics(self):
        """Test adding metrics to queue"""
        test_metrics = {
            "timestamp": "2025-03-04 18:39:39",
            "data": {
                "System": {
                    "cpu_usage": {
                        "value": 5.9,
                        "unit": "percent"
                    }
                }
            }
        }
        
        success = self.queue.send_metrics(test_metrics)
        self.assertTrue(success)
        self.assertEqual(len(self.queue.queue), 1)
    
    @patch('requests.post')
    def test_metrics_processing(self, mock_post):
        """Test metrics are properly processed and sent"""
        # Temporarily increase log level to suppress expected messages
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"message": "Metrics saved successfully"}
            mock_post.return_value = mock_response
            
            # Add test metrics
            test_metrics = {
                "timestamp": "2025-03-04 18:39:39",
                "data": {
                    "System": {
                        "cpu_usage": {
                            "value": 5.9,
                            "unit": "percent"
                        }
                    }
                }
            }
            
            self.queue.send_metrics(test_metrics)
            
            # Give time for processing
            time.sleep(0.5)
            
            # Verify request was made
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            self.assertEqual(call_args[1]['json'], test_metrics)
        finally:
            # Restore log level
            logging.getLogger().setLevel(self.original_level)

class TestPriorityQueue(unittest.TestCase):
    """Integration tests for PriorityQueue implementation"""
    
    def setUp(self):
        """Initialize queue before each test"""
        self.queue = PriorityMetricsQueue()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.queue.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        # Restore original logging level
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_queue_initialization(self):
        """Test priority queue is properly initialized"""
        self.assertIsNotNone(self.queue)
        self.assertTrue(self.queue.queue.empty())
    
    def test_priority_ordering(self):
        """Test metrics are processed in priority order"""
        # Add metrics with different priorities
        low_priority = {
            "timestamp": "2025-03-04 18:39:39",
            "data": {"Test": {"value": 1}}
        }
        high_priority = {
            "timestamp": "2025-03-04 18:39:39",
            "data": {"Test": {"value": 2}}
        }
        
        self.queue.send_metrics(low_priority, priority=2)
        self.queue.send_metrics(high_priority, priority=0)
        
        # Get items from queue
        priority1, _, metrics1 = self.queue.queue.get()
        priority2, _, metrics2 = self.queue.queue.get()
        
        # Verify high priority came first
        self.assertEqual(priority1, 0)
        self.assertEqual(metrics1["data"]["Test"]["value"], 2)
        self.assertEqual(priority2, 2)
        self.assertEqual(metrics2["data"]["Test"]["value"], 1)

if __name__ == '__main__':
    unittest.main() 