from src.config.config_loader import load_config
from src.logging.logger_setup import setup_logger
from ..models.metrics_model import MetricsModel
from src.client.simple_queue import SimpleQueue
from src.client.priority_queue import PriorityMetricsQueue
from src.utils.block_timer import BlockTimer
import time
from typing import Dict, List
from ..monitors.base_monitor import BaseMonitor

class MonitorHandler:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self._running = True
        self._paused = False
        self.last_metrics = None
        self.metrics_model = MetricsModel(self.config['app']['name'])
        self.monitors: List[BaseMonitor] = []
        self.metrics_queue = SimpleQueue()
    
    def pause_monitoring(self):
        """Pause all monitoring activities"""
        self._paused = True
        self.logger.info("Monitoring paused")
    
    def resume_monitoring(self):
        """Resume all monitoring activities"""
        self._paused = False
        self.logger.info("Monitoring resumed")
    
    def register_monitor(self, monitor: BaseMonitor) -> None:
        """Register a new monitor"""
        self.monitors.append(monitor)
        self.logger.debug(f"Registered monitor: {monitor.get_name()}")
    
    def collect_metrics(self) -> Dict:
        """Collect all metrics and return as structured data"""
        if self._paused:
            return None
        
        with BlockTimer("Complete metrics collection"):
            # Initialize all_metrics based on configured groups
            all_metrics = {group: {} for group in self.config['monitoring'] if isinstance(self.config['monitoring'][group], dict)}
            
            for monitor in self.monitors:
                try:
                    metrics = monitor.collect_metrics()
                    monitor.log_metrics(metrics)
                    
                    # Determine the group for the monitor using the configuration
                    for group, monitors in self.config['monitoring'].items():
                        if isinstance(monitors, dict) and monitor.get_name() in monitors:
                            all_metrics[group].update({monitor.get_name(): metrics})
                            break
                    else:
                        self.logger.warning(f"Monitor {monitor.get_name()} does not belong to any configured group")
                except Exception as e:
                    self.logger.error(f"Error collecting metrics from {monitor.get_name()}: {str(e)}")
            
            # Pass duration from BlockTimer to metrics model
            self.last_metrics = self.metrics_model.create_metrics_structure(
                all_metrics
            )
            
            # Send metrics to remote server if not paused
            if self.last_metrics and not self._paused:
                self.metrics_queue.send_metrics(self.last_metrics)
        
        return self.last_metrics
    
    def run(self):
        """Run the monitoring loop"""
        if not self.monitors:
            self.logger.error("No monitors registered")
            raise ValueError("No monitors registered. Please register at least one monitor.")
            
        self.logger.info("Starting monitoring service...")
        
        try:
            while self._running:
                try:
                    if not self._paused:
                        self.collect_metrics()
                    time.sleep(self.config['monitoring']['update_interval'])
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {str(e)}")
                    if self._running and not self._paused:
                        time.sleep(self.config['monitoring']['update_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received - stopping gracefully...")
            self.stop()
        finally:
            if self._running:  # If we haven't already stopped
                self.stop()
            self.logger.info("Monitoring service stopped")

    def stop(self):
        """Stop all monitors gracefully"""
        self.logger.debug("Stopping all monitors...")
        self._running = False
        
        # Stop each monitor
        for monitor in self.monitors:
            try:
                monitor.stop()
            except Exception as e:
                self.logger.error(f"Error stopping monitor {monitor.get_name()}: {str(e)}")
        
        self.logger.debug("All monitors stopped successfully")
        self.metrics_queue.stop()