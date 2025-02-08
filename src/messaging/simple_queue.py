from collections import deque
from threading import Thread, Event
import time
import json
import requests
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.block_timer import BlockTimer

class SimpleQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.queue = deque()
        self.stop_event = Event()
        
        self.logger.debug(f"Initialized metrics queue with server URL: {self.server_url}")
        
        # Start consumer thread
        self.consumer_thread = Thread(target=self._process_queue, daemon=True)
        self.consumer_thread.start()
        self.logger.debug("Started metrics processing thread")
        
    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Add metrics to queue"""
        try:
            with BlockTimer("Queue metrics"):
                self.logger.debug(f"Adding metrics to queue (current size: {len(self.queue)})")
                self.logger.debug(f"Metrics payload size: {len(json.dumps(metrics))} bytes")
                
                # Log key metrics being queued
                if 'data' in metrics:
                    for monitor_name, monitor_data in metrics['data'].items():
                        self.logger.debug(f"Queueing {monitor_name} metrics: {json.dumps(monitor_data, indent=2)}")
                
                self.queue.append(metrics)
                self.logger.debug(f"Metrics added to queue (new size: {len(self.queue)})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue metrics: {str(e)}")
            return False
            
    def _process_queue(self):
        """Process queued metrics in background"""
        while not self.stop_event.is_set():
            try:
                # Check if there are metrics to process
                if self.queue:
                    metrics = self.queue.popleft()
                    self.logger.debug(f"Processing metrics from queue (remaining: {len(self.queue)})")
                    
                    with BlockTimer("Send metrics from queue to PythonAnywhere"):
                        self.logger.debug(f"Sending metrics payload: {len(json.dumps(metrics))} bytes")
                        
                        # Log metrics being sent
                        if 'data' in metrics:
                            for monitor_name, monitor_data in metrics['data'].items():
                                self.logger.debug(f"Sending {monitor_name} metrics: {json.dumps(monitor_data, indent=2)}")
                        
                        response = requests.post(
                            self.server_url,
                            json=metrics,
                            headers={'Content-Type': 'application/json'}
                        )
                        response.raise_for_status()
                        
                        self.logger.debug(f"Server response status code: {response.status_code}")
                        self.logger.debug(f"Server response: {json.dumps(response.json(), indent=2)}")
                        
                else:
                    # No metrics to process, sleep briefly
                    time.sleep(0.1)
                    
            except requests.RequestException as e:
                self.logger.error(f"Failed to send metrics to PythonAnywhere: {str(e)}")
                if hasattr(e.response, 'text'):
                    self.logger.error(f"Server error response: {e.response.text}")
                # Put metrics back in queue
                self.queue.appendleft(metrics)
                self.logger.debug(f"Metrics returned to queue for retry (size: {len(self.queue)})")
                time.sleep(5)  # Wait before retrying
                
            except Exception as e:
                self.logger.error(f"Error processing queue: {str(e)}")
                time.sleep(1)
    
    def stop(self):
        """Stop the queue processor"""
        self.logger.debug("Stopping queue processor...")
        self.stop_event.set()
        self.consumer_thread.join(timeout=5)
        self.logger.debug(f"Queue processor stopped. Unprocessed items: {len(self.queue)}") 