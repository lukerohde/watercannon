#from gpiozero.pins.native import NativeFactory
from gpiozero import Device, AngularServo, OutputDevice
from time import sleep
import sys
import termios
import tty

# Initialize the servos and relay
#Device.pin_factory = NativeFactory()
servo1 = AngularServo(12, min_angle=0, max_angle=180,
                      min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo2 = AngularServo(13, min_angle=0, max_angle=180,
                      min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
relay = OutputDevice(17)

# Initialize angles
servo1_angle = 90  # Starting angle for servo1
servo2_angle = 90  # Starting angle for servo2

# Set initial positions
servo1.angle = servo1_angle
servo2.angle = servo2_angle

def activate_relay():
    relay.toggle()
    print("Relay toggled. Current state:", "ON" if relay.value else "OFF")

def move_servo1_left():
    global servo1_angle
    servo1_angle = max(0, servo1_angle - 15)
    servo1.angle = servo1_angle
    print(f"Servo1 moved left to {servo1_angle} degrees")

def move_servo1_right():
    global servo1_angle
    servo1_angle = min(180, servo1_angle + 15)
    servo1.angle = servo1_angle
    print(f"Servo1 moved right to {servo1_angle} degrees")

def move_servo2_up():
    global servo2_angle
    servo2_angle = min(180, servo2_angle + 10)
    servo2.angle = servo2_angle
    print(f"Servo2 moved up to {servo2_angle} degrees")

def move_servo2_down():
    global servo2_angle
    servo2_angle = max(0, servo2_angle - 10)
    servo2.angle = servo2_angle
    print(f"Servo2 moved down to {servo2_angle} degrees")

def getch():
    """Get a single character from standard input without echo."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Arrow keys
            ch += sys.stdin.read(2)  # Read the next two bytes
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

try:
    print("Controls:")
    print("- Press Space to toggle the relay.")
    print("- Use arrow keys to control the servos.")
    print("- Press 'q' to quit.")
    while True:
        ch = getch()
        if ch == ' ':
            activate_relay()
        elif ch == '\x1b[A':  # Up arrow
            move_servo2_up()
        elif ch == '\x1b[B':  # Down arrow
            move_servo2_down()
        elif ch == '\x1b[C':  # Right arrow
            move_servo1_right()
        elif ch == '\x1b[D':  # Left arrow
            move_servo1_left()
        elif ch == 'q':
            print("Exiting program.")
            servo1.close()
            servo2.close()
            relay.close()
            break
        sleep(0.1)  # Small delay to prevent high CPU usage

except KeyboardInterrupt:
    print("Program stopped by user.")
