from collections import deque
from threading import Thread, Event
import time
import json
import requests
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.block_timer import BlockTimer
from src.client.shutdown_handler import shutdown_handler

class SimpleQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.queue = deque()
        self.stop_event = Event()
        self._running = True
        
        self.logger.debug(f"Initialized metrics queue with server URL: {self.server_url}")
        
        # Start consumer thread
        self.consumer_thread = Thread(target=self._process_queue, daemon=True)
        self.consumer_thread.start()
        self.logger.debug("Started metrics processing thread")
        
    def _process_queue(self):
        """Process queued metrics in background"""
        while self._running:
            try:
                if not self.queue:
                    time.sleep(0.1)
                    continue
                    
                metrics = self.queue.popleft()
                self.logger.debug(f"Processing metrics from queue (remaining: {len(self.queue)})")
                
                with BlockTimer("Send metrics to server"):
                    response = requests.post(
                        self.server_url,
                        json=metrics,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Log successful metrics sending with cleaner message
                    self.logger.info(f"Metrics sent successfully. Shutdown status: {response_data.get('should_shutdown', False)}")
                    
                    # Check for shutdown command in response
                    if response_data.get('should_shutdown', False):
                        self.logger.info("Received shutdown command in metrics response")
                        shutdown_handler.handle_shutdown_request()
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to send metrics to server: {str(e)}")
                self.queue.appendleft(metrics)  # Put metrics back in queue
                time.sleep(5)  # Wait before retrying
                
            except Exception as e:
                self.logger.error(f"Error processing queue: {str(e)}")
                time.sleep(1)
        
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
            
    def stop(self):
        """Stop the queue processor"""
        self._running = False
        if self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0) 