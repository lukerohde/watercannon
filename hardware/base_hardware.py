# hardware/base_hardware.py

from abc import ABC, abstractmethod
import numpy as np
import time

class BaseHardwareController(ABC):
    """
    Base class for hardware controllers.
    """

    def __init__(self):
        # Common configuration
        
        self.pan_angle_home = 90
        self.pan_angle_high_limit = 180
        self.pan_angle_low_limit = 0
        self._set_pan_angle(self.pan_angle_home)
        
        self.tilt_angle_home = 60
        self.tilt_angle_high_limit = 120
        self.tilt_angle_low_limit = 20
        self._set_tilt_angle(self.tilt_angle_home)
        
        self.relay_on = False 

        self.activation_threshold_angle = 2
        self.last_tracking = None

        self._initialize_hardware()

    def process_signals(self, signals):
        """
        Activate hardware components based on signals.
        """
        if signals != None: 
            self.last_tracking = time.time()
            
            angle_x = signals.get('angle_x', 0)
            angle_y = signals.get('angle_y', 0)
            
            self._set_pan_angle(self.pan_angle + angle_x)
            self._set_tilt_angle(self.tilt_angle + angle_y)
            print(f'Targeting ({self.pan_angle}, {self.tilt_angle})')

            if abs(angle_x) < self.activation_threshold_angle and abs(angle_y) < self.activation_threshold_angle: 
                # stop moving and shoot
                self.activate_solenoid()
            else:
                self._update_servos()
                self.deactivate_solenoid()

            signals['relay_on'] = self.relay_on
                
    def patrol(self):
        self.deactivate_solenoid()
        if not self.last_tracking == None and time.time() - self.last_tracking > 5:
            self.last_tracking = None
            self._set_pan_angle(self.pan_angle_home)
            self._set_tilt_angle(self.tilt_angle_home)
            print(f'Returning home ({self.pan_angle}, {self.tilt_angle})')
            
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

    def _set_pan_angle(self, angle):
        self.pan_angle = np.clip(angle, self.pan_angle_low_limit, self.pan_angle_high_limit)
            

    def _set_tilt_angle(self, angle):
        self.tilt_angle = np.clip(angle, self.tilt_angle_low_limit, self.tilt_angle_high_limit)
            

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
