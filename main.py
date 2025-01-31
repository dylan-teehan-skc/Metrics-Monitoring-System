from src.metrics_monitoring.handlers.monitor_handler import MonitorHandler
from src.metrics_monitoring.monitors.system.system_monitor import SystemMonitor
from src.metrics_monitoring.monitors.crypto.btc_monitor import BTCMonitor
from src.metrics_monitoring.monitors.crypto.xrp_monitor import XRPMonitor

def main():
    # Create the monitor handler
    monitor = MonitorHandler()

    # Register monitors
    monitor.register_monitor(SystemMonitor())
    monitor.register_monitor(BTCMonitor())
    monitor.register_monitor(XRPMonitor())

    # Run the monitoring
    monitor.run()
    
if __name__ == "__main__":
    main()
