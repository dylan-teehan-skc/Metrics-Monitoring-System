"""Asynchronous queue for sending metrics"""
import asyncio
import aiohttp
import json
from typing import Dict, Any
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.client.shutdown_handler import shutdown_handler

class AsyncMetricsQueue:
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.queue = asyncio.Queue()
        self._running = True
        
        # Start queue processor
        self.loop = asyncio.get_event_loop()
        self.processor_task = self.loop.create_task(self._process_queue())
        
        self.logger.debug(f"Initialized async metrics queue with server URL: {self.server_url}")
        
    async def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Add metrics to queue"""
        try:
            self.logger.debug(f"Adding metrics to queue (current size: {self.queue.qsize()})")
            
            # Log key metrics being queued
            if 'data' in metrics:
                for monitor_name, monitor_data in metrics['data'].items():
                    self.logger.debug(f"Queueing {monitor_name} metrics: {json.dumps(monitor_data, indent=2)}")
            
            await self.queue.put(metrics)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to queue metrics: {str(e)}")
            return False
            
    async def _process_queue(self):
        """Process queued metrics in background"""
        async with aiohttp.ClientSession() as session:
            while self._running:
                try:
                    metrics = await self.queue.get()
                    self.logger.debug(f"Processing metrics from queue (remaining: {self.queue.qsize()})")
                    
                    async with session.post(
                        self.server_url,
                        json=metrics,
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        await response.raise_for_status()
                        response_data = await response.json()
                        
                        # Log successful metrics sending with cleaner message
                        self.logger.info(f"Metrics sent successfully. Shutdown status: {response_data.get('should_shutdown', False)}")
                        
                        # Check for shutdown command in response
                        if response_data.get('should_shutdown', False):
                            self.logger.info("Received shutdown command in metrics response")
                            shutdown_handler.handle_shutdown_request()
                        
                except aiohttp.ClientError as e:
                    self.logger.error(f"Failed to send metrics to server: {str(e)}")
                    await self.queue.put(metrics)
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Error processing queue: {str(e)}")
                    await asyncio.sleep(1)
                    
                finally:
                    self.queue.task_done()
    
    async def stop(self):
        """Stop the queue processor"""
        self._running = False
        await self.queue.join()  # Wait for all items to be processed
        self.processor_task.cancel()
        self.logger.debug(f"Queue processor stopped. Unprocessed items: {self.queue.qsize()}") 