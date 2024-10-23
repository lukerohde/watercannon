from adafruit_servokit import ServoKit
from gpiozero import OutputDevice
from time import sleep
import sys
import termios
import tty

# Initialize the ServoKit for PCA9685 (16 channels by default)
kit = ServoKit(channels=16)

# Initialize the servos on channels 0 and 1 (adjust channels as needed)
servo1 = kit.servo[0]
servo2 = kit.servo[1]
    
# Set pulse width range for servos (in microseconds)
servo1.set_pulse_width_range(500, 2500)  # 0.5ms to 2.5ms
servo2.set_pulse_width_range(500, 2500)

# Initialize the relay on GPIO pin 17
relay = OutputDevice(17)
relay.toggle()

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
        if ch == '\x1b':  # Arrow keys start with ESC
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
            break
        sleep(0.1)  # Small delay to prevent high CPU usage

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
finally:
    relay.close()