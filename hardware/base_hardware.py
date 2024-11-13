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
        
        self._pan_angle_high_limit = 180
        self._pan_angle_low_limit = 0
        
        self._tilt_angle_high_limit = 120
        self._tilt_angle_low_limit = 50
        
        self._relay_on = False 
        
         # Scanning pattern configuration
        self._scan_angles = [
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
        self._scan_target = 0
        self._scan_interval = 1.5
        self._tracking_pause = 5
        self._scan_interval_variation = 0
        self._pan_variation = 5
        self._tilt_variation = 3
        self._last_tracking = time.time() - self._tracking_pause
        self._last_scan = time.time() - self._scan_interval

        self._pan_angle = self._scan_angles[self._scan_target]['pan']
        self._tilt_angle = self._scan_angles[self._scan_target]['tilt']
        self._tilt = None
                
        # Smoothing stuff
        self._smooth_steps = 30
        self._smooth_thread = None 
        self._smooth_stop_event = threading.Event()

        self._frame_timestamp = time.time()
        
        self._initialize_hardware()

    def process_signals(self, tracker):
        """
        Activate hardware components based on signals.
        """
        loop_time = time.time() - self._frame_timestamp
        self._frame_timestamp = time.time()
        
        if tracker.target != None: 
            self._last_tracking = time.time()
            
            #self._smooth_pan(self._pan_angle + angle_x, self._tilt_angle + angle_y, loop_time)
            self._stop_smooth_pan()
            
            pan_angle = self._pan_angle + tracker.dx
            tilt_angle = self._tilt_angle + tracker.dy
            if tracker.fire: 
                self.activate_solenoid()
            
                if tracker.attack_angle() and tracker.attack_angle() > 90: 
                    if self._tilt == None:
                        self._tilt = self._tilt_angle # backup tilt angle prior to tilting up to fire
                    tilt_angle = tracker.attack_angle()
            else:
                self.deactivate_solenoid()

            self._set_pan_angle(pan_angle)
            self._set_tilt_angle(tilt_angle)
            self._update_servos() 

    def patrol(self):
        self.deactivate_solenoid()

        # after tilting up to fire, and loosing track of the target, restore original angle
        if self._tilt: 
            self._set_tilt_angle(self._tilt)
            self._update_servos()
            self._tilt = None
                
        if time.time() - self._last_tracking > self._tracking_pause: # wait 5 after being on target
            if time.time() - self._last_scan > self._scan_interval: # wait x before moving to next scan position
                self._last_scan = time.time()
                #scan_target = random.choice(self._scan_angles)

                self._scan_target = (self._scan_target + 1) % len(self._scan_angles)
                scan_target = self._scan_angles[self._scan_target]

                # Introduce slight random variations to make movement more organic
                pan_variation = random.uniform(-self._pan_variation, self._pan_variation)  
                tilt_variation = random.uniform(-self._tilt_variation, self._tilt_variation)

                self._smooth_pan(scan_target['pan'] + pan_variation, scan_target['tilt'] + tilt_variation, self._scan_interval)
                #self._set_pan_angle(scan_target['pan'] + pan_variation)
                #self._set_tilt_angle(scan_target['tilt'] + tilt_variation)
                self._update_servos()
                

    def activate_solenoid(self):
        """
        Activate the solenoid to squirt water.
        """
        if not self._relay_on:
            self._toggle_relay()
    
    def deactivate_solenoid(self):
        """
        Deactivate the solenoid to squirt water.
        """
        if self._relay_on:
            self._toggle_relay()
            
    def _log(self,str):
        print(str)

    def _set_pan_angle(self, angle):
        self._pan_angle = np.clip(angle, self._pan_angle_low_limit, self._pan_angle_high_limit)
            
    def _set_tilt_angle(self, angle):
        self._tilt_angle = np.clip(angle, self._tilt_angle_low_limit, self._tilt_angle_high_limit)

    def _stop_smooth_pan(self):
        if self._smooth_thread and self._smooth_thread.is_alive():
            self._smooth_stop_event.set()
            self._smooth_thread.join()
            self._smooth_stop_event.clear()
    
    def _smooth_pan(self, target_pan_angle, target_tilt_angle, scan_time):

        self._stop_smooth_pan()
        
        # Start a new thread for smooth panning
        self._smooth_thread = threading.Thread(
            target=self._smooth_pan_handler, 
            args=(target_pan_angle, target_tilt_angle, scan_time),
            daemon=True
        )
        self._smooth_thread.start()

    def _smooth_pan_handler(self, target_pan_angle, target_tilt_angle, scan_time):
        step_delay = scan_time / self._smooth_steps
        step_pan_angle = (target_pan_angle - self._pan_angle) / self._smooth_steps
        step_tilt_angle = (target_tilt_angle - self._tilt_angle) / self._smooth_steps

        for step in range(0, self._smooth_steps):
            if self._smooth_stop_event.is_set():
                break
            self._set_pan_angle(self._pan_angle + step_pan_angle)
            self._set_tilt_angle(self._tilt_angle + step_tilt_angle)
            self._update_servos()
            #print(self._pan_angle, self._tilt_angle)
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
