# hardware/pi_hardware.py
from .base_hardware import BaseHardwareController
from adafruit_servokit import ServoKit
from gpiozero import Device, OutputDevice

class PiHardwareServoKitController(BaseHardwareController):
    """
    Real hardware controller for Raspberry Pi.
    """

    def _initialize_hardware(self):
        """
        Initialize GPIO pins, servos, etc.
        """
        self._kit = ServoKit(channels=16)
        self._pan_servo = self._kit.servo[0]
        self._tilt_servo = self._kit.servo[1]
        self._pan_servo.set_pulse_width_range(550, 2600)  # 0.5ms to 2.5ms
        self._tilt_servo.set_pulse_width_range(550, 2600)
        self._pan_servo.angle = self._pan_angle
        self._tilt_servo.angle = self._tilt_angle

        self._solenoid_pin = 17
        self._solenoid_relay = OutputDevice(self._solenoid_pin)
        self._solenoid_relay.toggle()
        
        self._relay_on = not self._solenoid_relay.value 
        self.deactivate_solenoid()

    def _update_servos(self):
        """
        Update the current angles based on delta.
        """
        self._pan_servo.angle = self._pan_angle
        self._tilt_servo.angle = self._tilt_angle

    def _toggle_relay(self):
        self._solenoid_relay.toggle()
        self._relay_on = not self._solenoid_relay.value 

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        #self._pan_servo.close()
        #self._tilt_servo.close()
        self._solenoid_relay.close()
            





