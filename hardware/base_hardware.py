# hardware/base_hardware.py

from abc import ABC, abstractmethod
import numpy as np
import time
import random
import threading

class BaseHardwareController(ABC):
    """
    Base class for hardware controllers.
    """

    def __init__(self):
        # Common configuration
        
        self.pan_angle_high_limit = 180
        self.pan_angle_low_limit = 0
        
        self.tilt_angle_high_limit = 120
        self.tilt_angle_low_limit = 50
        
        self.relay_on = False 
        
         # Scanning pattern configuration
        self.scan_angles = [
            {'pan': 20, 'tilt': 70},
            {'pan': 55, 'tilt': 70},
            {'pan': 80, 'tilt': 80},
            {'pan': 95, 'tilt': 80},
            {'pan': 115, 'tilt': 70},
            {'pan': 130, 'tilt': 75},
            {'pan': 140, 'tilt': 75},
            {'pan': 155, 'tilt': 85}, 
            {'pan': 155, 'tilt': 85}, 
            {'pan': 160, 'tilt': 90},
            {'pan': 155, 'tilt': 86},
            {'pan': 130, 'tilt': 75},
            {'pan': 115, 'tilt': 70},
            {'pan': 95, 'tilt': 80},
            {'pan': 80, 'tilt': 80},
            {'pan': 55, 'tilt': 70},
            {'pan': 20, 'tilt': 70},
        ]
        self.scan_target = 0
        self.scan_interval = 1.5
        self.tracking_pause = 5
        self.scan_interval_variation = 0
        self.pan_variation = 5
        self.tilt_variation = 3
        self.last_tracking = time.time() - self.tracking_pause
        self.last_scan = time.time() - self.scan_interval

        self.pan_angle = self.scan_angles[self.scan_target]['pan']
        self.tilt_angle = self.scan_angles[self.scan_target]['tilt']
        
        # Smoothing stuff
        self.smooth_steps = 30
        self.smooth_thread = None 
        self.smooth_stop_event = threading.Event()

        self.frame_timestamp = time.time()
        
        self._initialize_hardware()

    def process_signals(self, signals):
        """
        Activate hardware components based on signals.
        """
        loop_time = time.time() - self.frame_timestamp
        self.frame_timestamp = time.time()
        
        if signals != None: 
            self.last_tracking = time.time()
            
            dx = signals.get('dx', 0)
            dy = signals.get('dy', 0)
            
            #self._smooth_pan(self.pan_angle + angle_x, self.tilt_angle + angle_y, loop_time)
            self._stop_smooth_pan()
            self._set_pan_angle(self.pan_angle + dx)
            self._set_tilt_angle(self.tilt_angle + dy)
            
            self._log(f'Targeting ({self.pan_angle}, {self.tilt_angle})')

            # TODO Move this 'on target' logic to target tracker, so it can aim up
            if signals.get('fire', 0) == 1: 
                # stop moving and shoot
                self.activate_solenoid()
            else:
                self._update_servos()
                self.deactivate_solenoid()

            signals['relay_on'] = self.relay_on
                

    def patrol(self):
        self.deactivate_solenoid()
        if time.time() - self.last_tracking > self.tracking_pause: # wait 5 after being on target
            if time.time() - self.last_scan > self.scan_interval: # wait x before moving to next scan position
        
                self.last_scan = time.time()
                #scan_target = random.choice(self.scan_angles)

                self.scan_target = (self.scan_target + 1) % len(self.scan_angles)
                scan_target = self.scan_angles[self.scan_target]

                # Introduce slight random variations to make movement more organic
                pan_variation = random.uniform(-self.pan_variation, self.pan_variation)  
                tilt_variation = random.uniform(-self.tilt_variation, self.tilt_variation)

                self._smooth_pan(scan_target['pan'] + pan_variation, scan_target['tilt'] + tilt_variation, self.scan_interval)
                #self._set_pan_angle(scan_target['pan'] + pan_variation)
                #self._set_tilt_angle(scan_target['tilt'] + tilt_variation)
                self._update_servos()
                

    def activate_solenoid(self):
        """
        Activate the solenoid to squirt water.
        """
        if not self.relay_on:
            self._toggle_relay()
    
    def deactivate_solenoid(self):
        """
        Deactivate the solenoid to squirt water.
        """
        if self.relay_on:
            self._toggle_relay()
            
    def _log(self,str):
        print(str)

    def _set_pan_angle(self, angle):
        self.pan_angle = np.clip(angle, self.pan_angle_low_limit, self.pan_angle_high_limit)
            
    def _set_tilt_angle(self, angle):
        self.tilt_angle = np.clip(angle, self.tilt_angle_low_limit, self.tilt_angle_high_limit)

    def _stop_smooth_pan(self):
        if self.smooth_thread and self.smooth_thread.is_alive():
            self.smooth_stop_event.set()
            self.smooth_thread.join()
            self.smooth_stop_event.clear()
    
    def _smooth_pan(self, target_pan_angle, target_tilt_angle, scan_time):

        self._stop_smooth_pan()
        
        # Start a new thread for smooth panning
        self.smooth_thread = threading.Thread(
            target=self._smooth_pan_handler, 
            args=(target_pan_angle, target_tilt_angle, scan_time),
            daemon=True
        )
        self.smooth_thread.start()

    def _smooth_pan_handler(self, target_pan_angle, target_tilt_angle, scan_time):
        step_delay = scan_time / self.smooth_steps
        step_pan_angle = (target_pan_angle - self.pan_angle) / self.smooth_steps
        step_tilt_angle = (target_tilt_angle - self.tilt_angle) / self.smooth_steps

        for step in range(0, self.smooth_steps):
            if self.smooth_stop_event.is_set():
                break
            self._set_pan_angle(self.pan_angle + step_pan_angle)
            self._set_tilt_angle(self.tilt_angle + step_tilt_angle)
            self._update_servos()
            #print(self.pan_angle, self.tilt_angle)
            time.sleep(step_delay)
        

    @abstractmethod
    def _initialize_hardware(self, signals):
        """Process signals to setup hardware components."""
        pass

    @abstractmethod
    def _update_servos(self, signals):
        """Process signals to control servos."""
        pass

    @abstractmethod
    def _toggle_relay(self, signals):
        """Process signals to control the relay."""
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up hardware resources."""
        pass
