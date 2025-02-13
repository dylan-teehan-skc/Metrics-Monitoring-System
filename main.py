from src.metrics_monitoring.handlers.monitor_handler import MonitorHandler
from src.metrics_monitoring.monitors.system.cpu_monitor import CPUMonitor
from src.metrics_monitoring.monitors.system.memory_monitor import MemoryMonitor
from src.metrics_monitoring.monitors.system.disk_monitor import DiskMonitor
from src.metrics_monitoring.monitors.system.process_monitor import ProcessMonitor
from src.metrics_monitoring.monitors.crypto.btc_monitor import BTCMonitor
from src.metrics_monitoring.monitors.crypto.xrp_monitor import XRPMonitor
from src.metrics_monitoring.monitors.weather.temperature_monitor import TemperatureMonitor
from src.metrics_monitoring.monitors.weather.humidity_monitor import HumidityMonitor

def main():
    monitorHandler = MonitorHandler()
    
    # Register monitors
    monitorHandler.register_monitor(CPUMonitor())
    monitorHandler.register_monitor(MemoryMonitor())
    monitorHandler.register_monitor(DiskMonitor())
    monitorHandler.register_monitor(ProcessMonitor())
    monitorHandler.register_monitor(BTCMonitor())
    monitorHandler.register_monitor(XRPMonitor())
    monitorHandler.register_monitor(TemperatureMonitor())
    monitorHandler.register_monitor(HumidityMonitor())

    monitorHandler.run()	
     
if __name__ == "__main__":
    main()
