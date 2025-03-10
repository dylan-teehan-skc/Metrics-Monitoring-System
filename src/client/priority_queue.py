from queue import PriorityQueue
from threading import Thread, Event
import time
import requests
from typing import Dict, Any, Tuple
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.block_timer import BlockTimer
from src.client.shutdown_handler import shutdown_handler

class PriorityMetricsQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.queue = PriorityQueue()
        self._running = True
        
        self.logger.debug(f"Initialized priority metrics queue with server URL: {self.server_url}")
        
        # Start consumer thread
        self.consumer_thread = Thread(target=self._process_queue, daemon=True)
        self.consumer_thread.start()
        self.logger.debug("Started metrics processing thread")
        
    def send_metrics(self, metrics: Dict[str, Any], priority: int = 1) -> bool:
        """
        Add metrics to queue with priority (lower number = higher priority)
        priority: 0 = high, 1 = normal, 2 = low
        """
        try:
            with BlockTimer("Queue metrics"):
                timestamp = time.time()  # Use timestamp to maintain FIFO within same priority
                self.logger.debug(f"Adding metrics to queue (current size: {self.queue.qsize()})")
                
                # Log key metrics being queued
                if 'data' in metrics:
                    for monitor_name, monitor_data in metrics['data'].items():
                        self.logger.debug(f"Queueing {monitor_name} metrics with priority {priority}")
                
                self.queue.put((priority, timestamp, metrics))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue metrics: {str(e)}")
            return False
            
    def _process_queue(self):
        """Process queued metrics in background, handling by priority"""
        while self._running:
            try:
                if self.queue.empty():
                    time.sleep(0.1)
                    continue
                    
                priority, timestamp, metrics = self.queue.get(timeout=1)
                self.logger.debug(f"Processing priority {priority} metrics from queue (remaining: {self.queue.qsize()})")
                
                with BlockTimer("Send metrics to server"):
                    response = requests.post(
                        self.server_url,
                        json=metrics,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Log successful metrics sending with cleaner message
                    self.logger.info(f"Metrics sent successfully. Priority: {priority}, Shutdown status: {response_data.get('should_shutdown', False)}")
                    
                    # Check for shutdown command in response
                    if response_data.get('should_shutdown', False):
                        self.logger.info("Received shutdown command in metrics response")
                        shutdown_handler.handle_shutdown_request()
                    
                    # Mark task as done
                    self.queue.task_done()
                    
            except requests.RequestException as e:
                self.logger.error(f"Failed to send metrics to server: {str(e)}")
                # Put metrics back in queue with same priority
                self.queue.put((priority, timestamp, metrics))
                time.sleep(5)  # Wait before retrying
                
            except Exception as e:
                self.logger.error(f"Error processing queue: {str(e)}")
                time.sleep(1)
    
    def stop(self):
        """Stop the queue processor"""
        self._running = False
        if self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0)