from src.config.config_loader import load_config
from src.logging.logger_setup import setup_logger
from ..models.metrics_model import MetricsModel
from src.messaging.async_queue import AsyncMetricsQueue
from src.utils.block_timer import BlockTimer
import asyncio
import time
from typing import Dict, List
from ..monitors.base_monitor import BaseMonitor

class MonitorHandler:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self._running = True
        self.last_metrics = None
        self.metrics_model = MetricsModel(self.config['app']['name'])
        self.monitors: List[BaseMonitor] = []
        self.metrics_queue = AsyncMetricsQueue()
        self.loop = asyncio.get_event_loop()
    
    def register_monitor(self, monitor: BaseMonitor) -> None:
        """Register a new monitor"""
        self.monitors.append(monitor)
        self.logger.debug(f"Registered monitor: {monitor.get_name()}")
    
    async def collect_metrics(self) -> Dict:
        """Collect all metrics and return as structured data"""
        self.logger.debug("Starting metrics collection...")
        
        with BlockTimer("Complete metrics collection"):
            all_metrics = {}
            for monitor in self.monitors:
                try:
                    metrics = monitor.collect_metrics()
                    monitor.log_metrics(metrics)
                    all_metrics[monitor.get_name()] = metrics
                except Exception as e:
                    self.logger.error(f"Error collecting metrics from {monitor.get_name()}: {str(e)}")
            
            self.last_metrics = self.metrics_model.create_metrics_structure(all_metrics)
            
            # Send metrics to queue
            if self.last_metrics:
                await self.metrics_queue.send_metrics(self.last_metrics)
        
        self.logger.debug("Metrics collection completed")
        return self.last_metrics
    
    async def run_async(self):
        """Run the monitoring loop asynchronously"""
        if not self.monitors:
            self.logger.error("No monitors registered")
            raise ValueError("No monitors registered. Please register at least one monitor.")
            
        self.logger.info("Starting monitoring service...")
        
        try:
            while self._running:
                try:
                    await self.collect_metrics()
                    await asyncio.sleep(self.config['monitoring']['update_interval'])
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {str(e)}")
                    if self._running:
                        await asyncio.sleep(self.config['monitoring']['update_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received - stopping gracefully...")
            await self.stop()
        finally:
            if self._running:
                await self.stop()
            self.logger.info("Monitoring service stopped")

    def run(self):
        """Run the monitoring loop"""
        self.loop.run_until_complete(self.run_async())
    
    async def stop(self):
        """Stop all monitors gracefully"""
        self.logger.debug("Stopping all monitors...")
        self._running = False
        
        # Stop each monitor
        for monitor in self.monitors:
            try:
                monitor.stop()
            except Exception as e:
                self.logger.error(f"Error stopping monitor {monitor.get_name()}: {str(e)}")
        
        # Stop queue
        await self.metrics_queue.stop()
        self.logger.debug("All monitors stopped successfully")