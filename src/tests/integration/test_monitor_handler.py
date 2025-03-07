"""
Integration tests for monitor handler.

This module tests the interaction between monitors and the monitor handler.
"""

import unittest
import logging
from src.metrics_monitoring.handlers.monitor_handler import MonitorHandler
from src.metrics_monitoring.monitors.system.cpu_monitor import CPUMonitor
from src.metrics_monitoring.monitors.system.memory_monitor import MemoryMonitor

class TestMonitorHandler(unittest.TestCase):
    """Integration tests for MonitorHandler"""
    
    def setUp(self):
        """Initialize handler and monitors"""
        self.handler = MonitorHandler()
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        # Store original logging level
        self.original_level = logging.getLogger().getEffectiveLevel()
        
    def tearDown(self):
        """Clean up resources"""
        self.handler.stop()
        
        # Clean up logger handlers
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def test_monitor_registration(self):
        """Test registering monitors with handler"""
        # Register monitors
        self.handler.register_monitor(self.cpu_monitor)
        self.handler.register_monitor(self.memory_monitor)
        
        # Verify monitors are registered
        self.assertEqual(len(self.handler.monitors), 2)
        self.assertIn(self.cpu_monitor, self.handler.monitors)
        self.assertIn(self.memory_monitor, self.handler.monitors)
    
    def test_metrics_collection(self):
        """Test collecting metrics from multiple monitors"""
        # Register monitors
        self.handler.register_monitor(self.cpu_monitor)
        self.handler.register_monitor(self.memory_monitor)
        
        # Collect metrics
        metrics = self.handler.collect_metrics()
        
        # Verify metrics structure
        self.assertIsNotNone(metrics)
        self.assertIn('data', metrics)
        self.assertIn('System', metrics['data'])
        self.assertIn('cpu_usage', metrics['data']['System'])
        self.assertIn('memory_usage', metrics['data']['System'])
    
    def test_monitor_stopping(self):
        """Test stopping all monitors"""
        # Register monitors
        self.handler.register_monitor(self.cpu_monitor)
        self.handler.register_monitor(self.memory_monitor)
        
        # Stop handler
        self.handler.stop()
        
        # Verify monitors are stopped
        self.assertFalse(self.cpu_monitor.is_running())
        self.assertFalse(self.memory_monitor.is_running())

if __name__ == '__main__':
    unittest.main() 