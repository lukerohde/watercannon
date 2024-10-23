# temperature_monitor.py

import os
import time
import threading
from collections import deque

class TemperatureMonitor:
    """
    Monitors the Raspberry Pi CPU temperature and signals when it exceeds a threshold.
    """
    
    def __init__(self, stable_threshold=70.0, max_threshold=80, check_interval=1, throttle_time=0.5, avg_window=3):
        """
        Initialize the TemperatureMonitor.
        """
        self.stable_threshold = stable_threshold
        self.max_threshold = max_threshold
        self.check_interval = check_interval
        self.throttle_time = throttle_time
        self.overheat_event = threading.Event()
        self.stop_event = threading.Event()
        self.avg_window = avg_window
        self.thread = threading.Thread(target=self._monitor_temperature, daemon=True)
        self.temp_readings = deque(maxlen=self.avg_window)  # For moving average
    

    def get_cpu_temp(self):
        """Reads the CPU temperature."""
        temp_str = os.popen("vcgencmd measure_temp").readline()
        return float(temp_str.replace("temp=", "").replace("'C\n", ""))
    
    def throttle(self):
        while self.overheat_event.is_set():
            time.sleep(1)
            continue
        time.sleep(self.throttle_time)

    def _monitor_temperature(self):
        """Continuously monitors the CPU temperature."""
        last_avg_temp=None
        while not self.stop_event.is_set():

            temp = self.get_cpu_temp()
            self.temp_readings.append(temp)
            avg_temp = sum(self.temp_readings) / len(self.temp_readings)
            
            if avg_temp >= self.max_threshold:
                print(f"[TemperatureMonitor] Overheating detected! Temperature: {temp}°C >= {self.max_threshold}°C")
                self.overheat_event.set()
            
            if avg_temp >= self.stable_threshold:
                if last_avg_temp != None and avg_temp > last_avg_temp and avg_temp > self.stable_threshold + 3 : 
                    self.throttle_time *= 1.3
                    print(f"[TemperatureMonitor] Current Temperature: {temp}°C - increasing throttling {self.throttle_time}s")
            
                time.sleep(self.throttle_time)
                last_avg_temp = avg_temp

            else:
                if last_avg_temp != None:
                    print(f"[TemperatureMonitor] Current Temperature: {temp}°C - reducing throttling {self.throttle_time}s")
            
                    last_avg_temp = None
                    self.throttle_time /= 1.1 
                    self.overheat_event.clear()

            time.sleep(self.check_interval)
            
    def start(self):
        """Starts the temperature monitoring thread."""
        self.thread.start()
    
    def stop(self):
        """Stops the temperature monitoring thread."""
        self.stop_event.set()
        self.thread.join()