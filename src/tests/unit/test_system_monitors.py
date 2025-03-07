"""
Unit tests for system monitoring components.

This module contains unit tests for CPU, Memory, and Process monitors.
"""

import unittest
from unittest.mock import Mock, patch
import logging
from src.metrics_monitoring.monitors.system.cpu_monitor import CPUMonitor
from src.metrics_monitoring.monitors.system.memory_monitor import MemoryMonitor
from src.metrics_monitoring.monitors.system.process_monitor import ProcessMonitor

class TestSystemMonitors(unittest.TestCase):
    """Test cases for system monitoring components"""
    
    def setUp(self):
        """Initialize monitors before each test"""
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.process_monitor = ProcessMonitor()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.cpu_monitor.stop()
        self.memory_monitor.stop()
        self.process_monitor.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_monitor_initialization(self):
        """Test that monitors are properly initialized"""
        self.assertIsNotNone(self.cpu_monitor)
        self.assertIsNotNone(self.memory_monitor)
        self.assertIsNotNone(self.process_monitor)
        
        # Verify monitor names
        self.assertEqual(self.cpu_monitor.get_name(), "cpu_usage")
        self.assertEqual(self.memory_monitor.get_name(), "memory_usage")
        self.assertEqual(self.process_monitor.get_name(), "process_count")
    
    @patch('psutil.cpu_percent')
    def test_cpu_metrics_collection(self, mock_cpu_percent):
        """Test CPU metrics collection"""
        # Setup mock CPU usage
        mock_cpu_percent.return_value = 45.5
        
        # Collect metrics
        metrics = self.cpu_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 45.5)
        self.assertEqual(metrics['unit'], 'percent')
    
    @patch('psutil.virtual_memory')
    def test_memory_metrics_collection(self, mock_virtual_memory):
        """Test memory metrics collection"""
        # Setup mock memory usage
        mock_memory = Mock()
        mock_memory.percent = 75.2
        mock_virtual_memory.return_value = mock_memory
        
        # Collect metrics
        metrics = self.memory_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 75.2)
        self.assertEqual(metrics['unit'], 'percent')
    
    @patch('psutil.pids')
    def test_process_metrics_collection(self, mock_pids):
        """Test process count metrics collection"""
        # Setup mock process list
        mock_pids.return_value = list(range(100))  # Simulate 100 processes
        
        # Collect metrics
        metrics = self.process_monitor.collect_metrics()
        
        # Verify metrics format and values
        self.assertIn('value', metrics)
        self.assertIn('unit', metrics)
        self.assertEqual(metrics['value'], 100)
        self.assertEqual(metrics['unit'], 'count')

if __name__ == '__main__':
    unittest.main() 