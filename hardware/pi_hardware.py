# hardware/pi_hardware.py
from .base_hardware import BaseHardwareController
from gpiozero import Device, AngularServo, OutputDevice

class PiHardwareController(BaseHardwareController):
    """
    Real hardware controller for Raspberry Pi.
    """

    def _initialize_hardware(self):
        """
        Initialize GPIO pins, servos, etc.
        """
        self.solenoid_pin = 17
        self.pan_servo_pin = 12
        self.tilt_servo_pin = 13

        self.pan_servo = AngularServo(self.pan_servo_pin, min_angle=0, max_angle=self.pan_angle_limit,
                            min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
        self.tilt_servo = AngularServo(self.tilt_servo_pin, min_angle=0, max_angle=self.pan_angle_limit,
                            min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
        self.solenoid_relay = OutputDevice(self.solenoid_pin)

        self.relay_on = self.solenoid_relay.value 
        self.deactivate_solenoid()


    def _update_servos(self):
        """
        Update the current angles based on delta.
        """
        self.pan_servo.angle = self.pan_angle
        self.tilt_servo.angle = self.tilt_angle

    def _toggle_relay(self):
        self.solenoid_relay.toggle()
        self.relay_on = self.solenoid_relay.value 

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        self.pan_servo.close()
        self.tilt_servo.close()
        self.solenoid_relay.close()
            





