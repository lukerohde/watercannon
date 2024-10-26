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
        self.kit = ServoKit(channels=16)
        self.pan_servo = self.kit.servo[0]
        self.tilt_servo = self.kit.servo[1]
        self.pan_servo.set_pulse_width_range(550, 2600)  # 0.5ms to 2.5ms
        self.tilt_servo.set_pulse_width_range(550, 2600)
        self.pan_servo.angle = self.pan_angle
        self.tilt_servo.angle = self.tilt_angle

        self.solenoid_pin = 17
        self.solenoid_relay = OutputDevice(self.solenoid_pin)
        self.solenoid_relay.toggle()
        
        self.relay_on = not self.solenoid_relay.value 
        self.deactivate_solenoid()

    def _update_servos(self):
        """
        Update the current angles based on delta.
        """
        self.pan_servo.angle = self.pan_angle
        self.tilt_servo.angle = self.tilt_angle

    def _toggle_relay(self):
        self.solenoid_relay.toggle()
        self.relay_on = not self.solenoid_relay.value 

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        #self.pan_servo.close()
        #self.tilt_servo.close()
        self.solenoid_relay.close()
            





