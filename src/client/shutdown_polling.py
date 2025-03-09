import tkinter as tk
from tkinter import messagebox
import logging
import os
import sys
import signal
import requests
import threading
import time
from typing import Optional
from src.logging.logger_setup import setup_logger
from src.config.config_loader import load_config
import subprocess

# Disable urllib3 debug logging
logging.getLogger("urllib3").setLevel(logging.WARNING)

class ShutdownPolling:
    _instance: Optional['ShutdownPolling'] = None
    _lock = threading.Lock()  # Class level lock for thread safety
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize or reinitialize the polling instance"""
        # Always reinitialize to ensure clean state
        self.config = load_config()
        self.logger = setup_logger(self.config)
        self.server_url = self.config['server']['url']
        self.initialized = True
        self.monitor_handler = None  # Will be set from main.py
        self._shutdown_in_progress = False  # Flag to track shutdown state
    
    def set_monitor_handler(self, handler):
        """Set the monitor handler reference"""
        self.monitor_handler = handler
    
    def handle_shutdown_request(self):
        """Handle a shutdown request from the metrics queue"""
        with self._lock:
            if self._shutdown_in_progress:
                self.logger.info("Shutdown already in progress, ignoring additional request")
                return
                
            self._shutdown_in_progress = True
            
        self.logger.info("Received shutdown command")
        # Pause monitoring
        if self.monitor_handler:
            self.logger.info("Pausing all monitoring...")
            self.monitor_handler.pause_monitoring()
        
        try:
            # Show popup and wait for user confirmation
            if self.show_shutdown_popup():
                self.logger.info("User accepted shutdown")
                self.handle_shutdown()
            else:
                self.logger.info("User cancelled shutdown")
                # Resume monitoring
                if self.monitor_handler:
                    self.monitor_handler.resume_monitoring()
                with self._lock:
                    self._shutdown_in_progress = False
        except Exception as e:
            self.logger.error(f"Error during shutdown process: {str(e)}")
            with self._lock:
                self._shutdown_in_progress = False
            if self.monitor_handler:
                self.monitor_handler.resume_monitoring()
    
    def show_shutdown_popup(self):
        """Shows a Tkinter popup notification about the client shutdown"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Bring window to front and ensure it stays there
            root.lift()
            root.attributes('-topmost', True)
            
            # Show confirmation dialog and wait for user response
            result = messagebox.askokcancel(
                "Shutdown Required",
                "Server has requested a shutdown. Click OK to proceed with shutdown.",
                parent=root
            )
            root.destroy()
            return result
        except Exception as e:
            self.logger.error(f"Failed to show shutdown popup: {str(e)}")
            return True  # Default to allowing shutdown if popup fails
    
    def handle_shutdown(self):
        """Handle shutdown command"""
        try:
            self.logger.info("Initiating client shutdown...")
            
            # Reset the singleton instance before exit
            ShutdownPolling._instance = None
            
            # Exit the current process
            os._exit(0)  # Force exit to avoid any cleanup issues
                
        except Exception as e:
            self.logger.error(f"Failed to shutdown client: {str(e)}")
            with self._lock:
                self._shutdown_in_progress = False

# Create a singleton instance
shutdown_polling = ShutdownPolling()

# Log successful restart only if this is a restart (not initial start)
if os.environ.get('RESTARTED') == '1':
    shutdown_polling.logger.info("Successfully restarted client") 