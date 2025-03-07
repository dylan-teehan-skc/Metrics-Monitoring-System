from queue import PriorityQueue
from threading import Thread, Event
import time
import json
import requests
from typing import Dict, Any, Tuple
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.block_timer import BlockTimer
from datetime import datetime

class PriorityMetricsQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        # Using PriorityQueue instead of deque - (priority, timestamp, metrics)
        self.queue = PriorityQueue()
        self.stop_event = Event()
        
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
                self.logger.debug(f"Metrics payload size: {len(json.dumps(metrics))} bytes")
                
                # Log key metrics being queued
                if 'data' in metrics:
                    for monitor_name, monitor_data in metrics['data'].items():
                        self.logger.debug(f"Queueing {monitor_name} metrics with priority {priority}: {json.dumps(monitor_data, indent=2)}")
                
                self.queue.put((priority, timestamp, metrics))
                self.logger.debug(f"Metrics added to queue (new size: {self.queue.qsize()})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue metrics: {str(e)}")
            return False
            
    def _process_queue(self):
        """Process queued metrics in background, handling by priority"""
        while not self.stop_event.is_set():
            try:
                # Check if there are metrics to process
                if not self.queue.empty():
                    priority, timestamp, metrics = self.queue.get(timeout=1)
                    self.logger.debug(f"Processing priority {priority} metrics from queue (remaining: {self.queue.qsize()})")
                    
                    with BlockTimer("Send metrics to PythonAnywhere") as timer:
                        self.logger.debug(f"Sending metrics payload: {len(json.dumps(metrics))} bytes")
                        
                        # Log the payload being sent
                        self.logger.debug(f"Payload being sent: {json.dumps(metrics, indent=2)}")
                        
                        response = requests.post(
                            self.server_url,
                            json=metrics,
                            headers={'Content-Type': 'application/json'}
                        )
                        response.raise_for_status()
                        
                        self.logger.info(f"Successfully sent priority {priority} metrics to PythonAnywhere")
                        self.logger.debug(f"Server response status code: {response.status_code}")
                        self.logger.debug(f"Server response: {json.dumps(response.json(), indent=2)}")
                        
                        # Mark task as done
                        self.queue.task_done()
                        
                else:
                    # No metrics to process, sleep briefly
                    time.sleep(0.1)
                    
            except requests.RequestException as e:
                self.logger.error(f"Failed to send metrics to PythonAnywhere: {str(e)}")
                if hasattr(e.response, 'text'):
                    self.logger.error(f"Server error response: {e.response.text}")
                # Put metrics back in queue with same priority
                self.queue.put((priority, timestamp, metrics))
                self.logger.debug(f"Metrics returned to queue for retry (size: {self.queue.qsize()})")
                time.sleep(5)  # Wait before retrying
                
            except Exception as e:
                self.logger.error(f"Error processing queue: {str(e)}")
                time.sleep(1)
    
    def stop(self):
        """Stop the queue processor"""
        self.logger.debug("Stopping queue processor...")
        self.stop_event.set()
        self.consumer_thread.join(timeout=5)
        self.logger.debug(f"Queue processor stopped. Unprocessed items: {self.queue.qsize()}")