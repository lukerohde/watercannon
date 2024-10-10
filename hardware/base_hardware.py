# hardware/base_hardware.py

from abc import ABC, abstractmethod
import numpy as np

class BaseHardwareController(ABC):
    """
    Base class for hardware controllers.
    """

    def __init__(self):
        # Common configuration

        self.pan_angle = 90  
        self.pan_angle_limit = 180
        self.tilt_angle = 90 
        self.tilt_angle_limit = 180
        self.relay_on = False 

        self.activation_threshold_angle = 3

        self._initialize_hardware()

    def process_signals(self, signals):
        """
        Activate hardware components based on signals.
        """
        if signals != None: 
            angle_x = signals.get('angle_x', 0)
            angle_y = signals.get('angle_y', 0)
            
            self.pan_angle = np.clip(self.pan_angle + angle_x, 0, self.pan_angle_limit)
            self.tilt_angle = np.clip(self.tilt_angle + angle_y, 0, self.tilt_angle_limit)
                
            if abs(angle_x) < self.activation_threshold_angle and abs(angle_y) < self.activation_threshold_angle: 
                # stop moving and shoot
                self.activate_solenoid()
            else:
                self._update_servos()
                self.deactivate_solenoid()

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
