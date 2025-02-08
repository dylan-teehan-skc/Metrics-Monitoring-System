"""Asynchronous queue for sending metrics"""
import asyncio
import aiohttp
import json
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.utils.block_timer import BlockTimer

class AsyncMetricsQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.queue = asyncio.Queue()
        self.running = True
        
        # Start queue processor
        self.loop = asyncio.get_event_loop()
        self.processor_task = self.loop.create_task(self._process_queue())
        
        self.logger.debug(f"Initialized async metrics queue with server URL: {self.server_url}")
        
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Add metrics to queue"""
        try:
            with BlockTimer("Queue metrics"):
                self.logger.debug(f"Adding metrics to queue (current size: {self.queue.qsize()})")
                self.logger.debug(f"Metrics payload size: {len(json.dumps(metrics))} bytes")
                
                # Log key metrics being queued
                if 'data' in metrics:
                    for monitor_name, monitor_data in metrics['data'].items():
                        self.logger.debug(f"Queueing {monitor_name} metrics: {json.dumps(monitor_data, indent=2)}")
                
                await self.queue.put(metrics)
                self.logger.debug(f"Metrics added to queue (new size: {self.queue.qsize()})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue metrics: {str(e)}")
            return False
            
    async def _process_queue(self):
        """Process queued metrics in background"""
        async with aiohttp.ClientSession() as session:
            while self.running:
                try:
                    # Get metrics from queue
                    metrics = await self.queue.get()
                    self.logger.debug(f"Processing metrics from queue (remaining: {self.queue.qsize()})")
                    
                    with BlockTimer("Send metrics to PythonAnywhere"):
                        self.logger.debug(f"Sending metrics payload: {len(json.dumps(metrics))} bytes")
                        
                        # Log metrics being sent
                        if 'data' in metrics:
                            for monitor_name, monitor_data in metrics['data'].items():
                                self.logger.debug(f"Sending {monitor_name} metrics: {json.dumps(monitor_data, indent=2)}")
                        
                        async with session.post(
                            self.server_url,
                            json=metrics,
                            headers={'Content-Type': 'application/json'}
                        ) as response:
                            await response.raise_for_status()
                            response_data = await response.json()
                            
                            self.logger.debug(f"Server response status code: {response.status}")
                            self.logger.debug(f"Server response: {json.dumps(response_data, indent=2)}")
                            
                except aiohttp.ClientError as e:
                    self.logger.error(f"Failed to send metrics to PythonAnywhere: {str(e)}")
                    # Put metrics back in queue
                    await self.queue.put(metrics)
                    self.logger.debug(f"Metrics returned to queue for retry (size: {self.queue.qsize()})")
                    await asyncio.sleep(5)  # Wait before retrying
                    
                except Exception as e:
                    self.logger.error(f"Error processing queue: {str(e)}")
                    await asyncio.sleep(1)
                    
                finally:
                    self.queue.task_done()
    
    async def stop(self):
        """Stop the queue processor"""
        self.logger.debug("Stopping async queue processor...")
        self.running = False
        await self.queue.join()  # Wait for all items to be processed
        self.processor_task.cancel()
        self.logger.debug(f"Queue processor stopped. Unprocessed items: {self.queue.qsize()}") 