import tkinter as tk
from tkinter import messagebox
import logging
import os
import requests
import threading
from typing import Optional
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
from src.metrics_monitoring.models.base_template import DefaultTemplate
import json

class ShutdownHandler:
    _instance: Optional['ShutdownHandler'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = load_config()
            self.logger = setup_logger(self.config)
            self.server_url = self.config['server']['url']
            self.monitor_handler = None
            self._shutdown_in_progress = False
            self.initialized = True
    
    def set_monitor_handler(self, handler):
        """Set the monitor handler reference"""
        self.monitor_handler = handler
    
    def handle_shutdown_request(self):
        """Handle a shutdown request from the metrics response"""
        with self._lock:
            if self._shutdown_in_progress:
                self.logger.info("Shutdown already in progress")
                return
            self._shutdown_in_progress = True
        
        self.logger.info("Processing shutdown request")
        if self.monitor_handler:
            self.logger.info("Pausing monitoring...")
            self.monitor_handler.pause_monitoring()
        
        try:
            if self.show_shutdown_popup():
                self.logger.info("User accepted shutdown")
                self._perform_shutdown()
            else:
                self.logger.info("User cancelled shutdown")
                self.cancel_shutdown()
                if self.monitor_handler:
                    self.monitor_handler.resume_monitoring()
                with self._lock:
                    self._shutdown_in_progress = False
        except Exception as e:
            self.logger.error(f"Error during shutdown process: {str(e)}")
            if self.monitor_handler:
                self.monitor_handler.resume_monitoring()
            with self._lock:
                self._shutdown_in_progress = False
    
    def cancel_shutdown(self):
        """Cancel the shutdown request on the server"""
        try:
            mac_address = DefaultTemplate().mac_address
            self.logger.info(f"Cancelling shutdown for client {mac_address}")
            
            base_url = self.server_url.split('/v1.0')[0]
            response = requests.post(
                f"{base_url}/api/cancel-shutdown",
                params={"client_id": mac_address},
                timeout=5
            )
            response.raise_for_status()
            self.logger.info("Shutdown cancelled successfully")
        except Exception as e:
            self.logger.error(f"Failed to cancel shutdown: {str(e)}")
    
    def show_shutdown_popup(self) -> bool:
        """Show shutdown confirmation popup"""
        try:
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            
            result = messagebox.askokcancel(
                "Shutdown Required",
                "Server has requested a shutdown. Click OK to proceed with shutdown.",
                parent=root
            )
            root.destroy()
            self.logger.info(f"User response to shutdown: {'accepted' if result else 'cancelled'}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to show shutdown popup: {str(e)}")
            return False
    
    def _perform_shutdown(self):
        """Perform the actual shutdown"""
        try:
            self.logger.info("Initiating shutdown...")
            ShutdownHandler._instance = None
            os._exit(0)
        except Exception as e:
            self.logger.error(f"Failed to shutdown: {str(e)}")
            with self._lock:
                self._shutdown_in_progress = False

# Singleton instance
shutdown_handler = ShutdownHandler() 