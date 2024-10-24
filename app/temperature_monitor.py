# temperature_monitor.py

import os
import time
import threading
from collections import deque

class TemperatureMonitor:
    """
    Monitors the Raspberry Pi CPU temperature and signals when it exceeds a threshold.
    """
    
    def __init__(self,  max_temp=84, stable_temp=79.0, stable_temp_window=3.0, check_interval=1, moving_avg_readings=3, starting_throttle_time=0.1,  throttle_up_multiplier=1.3, throttle_down_divisor=1.1):
        """
        Initialize the TemperatureMonitor.
        """
        self.stable_temp = stable_temp
        self.max_temp = max_temp
        self.check_interval = check_interval
        self.throttle_time = None
        self.starting_throttle_time = starting_throttle_time
        self.stable_temp_window = stable_temp_window
        self.moving_avg_readings = moving_avg_readings
        self.throttle_up_multiplier = throttle_up_multiplier
        self.throttle_down_divisor = throttle_down_divisor
        
        
        self.overheat_event = threading.Event()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._monitor_temperature, daemon=True)
        self.temp_readings = deque(maxlen=self.moving_avg_readings)  # For moving average
        self.throttle_lock = threading.Lock()
    

    def get_cpu_temp(self):
        """Reads the CPU temperature."""
        temp_str = os.popen("vcgencmd measure_temp").readline()
        return float(temp_str.replace("temp=", "").replace("'C\n", ""))
    
    def throttle(self):
        while self.overheat_event.is_set():
            self._halt() # just stop everything until the temperature dips back down

        with self.throttle_lock:
            t = self.throttle_time

        if t is not None:
            self._slowdown(t)

    def _halt(self):
        """Defined just for testing"""
        time.sleep(1)

    def _slowdown(self, t):
        """Defined just for testing"""
        time.sleep(t)

    def _log(self, str):
        print(str)

    def _monitor_temperature(self):
        """Continuously monitors the CPU temperature."""
        avg_temp=None
        while not self.stop_event.is_set():
            last_avg_temp = avg_temp
            temp = self.get_cpu_temp()
            self.temp_readings.append(temp)
            avg_temp = sum(self.temp_readings) / len(self.temp_readings)
            
            if avg_temp is not None and avg_temp >= self.max_temp:
                if not self.overheat_event.is_set():
                    self._log(f"[TemperatureMonitor] Overheating detected! Average Temperature: {avg_temp:.1f}°C >= {self.max_temp}°C")
                    self.overheat_event.set()
            else:
                if self.overheat_event.is_set():
                    self._log(f"[TemperatureMonitor] Overheating cleared! Average Temperature: {avg_temp:.1f}°C < {self.max_temp}°C")
                    self.overheat_event.clear() 
                    
            with self.throttle_lock: 
                if last_avg_temp is not None:
                    # not cooling and over threshold window
                    if avg_temp >= last_avg_temp and avg_temp > self.stable_temp + self.stable_temp_window/2.0:  
                        if self.throttle_time is None: 
                            self.throttle_time = self.starting_throttle_time 
                        else:
                            self.throttle_time *= self.throttle_up_multiplier
                        self._log(f"[TemperatureMonitor] Average Temperature: {avg_temp:.1f}°C - increasing throttling {self.throttle_time:.2f}s")
                    
                    # not heating and under threshold window
                    if self.throttle_time is not None and avg_temp <= last_avg_temp and avg_temp < self.stable_temp - self.stable_temp_window/2.0: 
                        self.throttle_time /= self.throttle_down_divisor
                        if self.throttle_time < self.starting_throttle_time:
                            self.throttle_time = None
                        
                        self._log(f"[TemperatureMonitor] Average Temperature: {avg_temp:.1f}°C - decreasing throttling {(self.throttle_time or 0):.2f}s")
                
            time.sleep(self.check_interval)
            
    def start(self):
        """Starts the temperature monitoring thread."""
        self.thread.start()
    
    def stop(self):
        """Stops the temperature monitoring thread."""
        self.stop_event.set()
        self.thread.join()