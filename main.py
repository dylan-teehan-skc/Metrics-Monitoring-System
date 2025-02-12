from src.metrics_monitoring.handlers.monitor_handler import MonitorHandler
from src.metrics_monitoring.monitors.system.cpu_monitor import CPUMonitor
from src.metrics_monitoring.monitors.system.memory_monitor import MemoryMonitor
from src.metrics_monitoring.monitors.crypto.btc_monitor import BTCMonitor
from src.metrics_monitoring.monitors.crypto.xrp_monitor import XRPMonitor

def main():
    monitorHandler = MonitorHandler()

    # Register monitors
    monitorHandler.register_monitor(CPUMonitor())
    monitorHandler.register_monitor(MemoryMonitor())
    monitorHandler.register_monitor(BTCMonitor())
    monitorHandler.register_monitor(XRPMonitor())

    monitorHandler.run()	
     
if __name__ == "__main__":
    main()
