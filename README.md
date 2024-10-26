WATERCANNON - README

AUTOMATED ANTI-CHICKEN DEVICE
=============================

![Project Logo](path/to/logo.png)

Table of Contents
-----------------

*   [Overview](#overview)
*   [Features](#features)
*   [Hardware](#hardware)
    *   [Parts List](#parts-list)
    *   [Hardware Breakdown](#hardware-breakdown)
    *   [Schematics](#schematics)
*   [Installation](#installation)
    *   [Prerequisites](#prerequisites)
    *   [Setup on Mac](#setup-on-mac)
    *   [Setup on Raspberry Pi](#setup-on-raspberry-pi)
*   [Running the Application](#running-the-application)
    *   [Activate Virtual Environment](#activate-virtual-environment)
    *   [Start the App](#start-the-app)
    *   [Accessing the Camera Feed](#accessing-the-camera-feed)
*   [Testing](#testing)
    *   [Automatic Test Runner](#automatic-test-runner)
    *   [Manual Testing](#manual-testing)
*   [Directory Structure](#directory-structure)
*   [How It Works](#how-it-works)
*   [Contribution](#contribution)
*   [License](#license)
*   [ShoutOuts](#shout-outs)
*   [Disclaimer](#disclaimer)

Overview
--------

**WaterCannon** is a hobby project designed to keep birds - especially chickens - from pooping on my newly built deck.  It detects birds using computer vision and automatically targets and sprays them with water. 

The system leverages a Raspberry Pi 5 for processing and controlling hardware components, providing real-time video streaming via a Flask web server. 

This project is ideal for poultry enthusiasts looking to implement automated solutions for managing their flocks.  It could be adapted to deter cats on benches or barking dogs.  

Features
--------

*   **Real-Time Detection:** Utilizes computer vision to detect chickens in live video feeds.
*   **Automated Tracking and Targeting:** Controls a two pan and tilt servos when a chicken is detected
*   **Automated Spraying:** Controls a solenoid valve to spray water when a chicken is in its sights.
*   **Multi-Platform Support:** Compatible with both Raspberry Pi and Mac for development and deployment.
*   **Flask Web Server:** Streams processed video to clients, allowing remote monitoring.
*   **Thread-Safe Frame Processing:** Ensures reliable and efficient processing of video frames.
*   **Overheat protection:** Throttles the frame rate if the cpu temp is getting too high.
*   **Sentry mode:** Pan's around a programmable path so nothing can sneak past.
*   **Sleep mode:** Sleep when it gets too dark, or is covered
*   **Fire control:** Prevent it spraying too much or if people are in the way
*   **Testing Support:** Includes fake hardware and camera modules for robust unit testing.

TO DO
--------
* Testing of Sleep Mode (inc fixing tests), Smooth Panning and Fire Control
* Parameterisation of Sentry Mode and Fire Control
* Refactor of Fire Control so its managed by Targeting and can avoid people
* Aim up for more accurate and longer range firing
* Record history of firing events
* Discriminate between deck chickens and lawn chickens

Hardware
--------

### Parts List

The following items were purchased from [http://core-electronics.com.au](https://core-electronics.com.au)

1.  **FIT0415** - FPV Nylon Pan & Tilt Kit (Without Servo)
2.  **CE09785** - Raspberry Pi 5 Model B 4GB
3.  **CE09789** - Raspberry Pi 5 Case, Red/White (Official)
4.  **CE09791** - Raspberry Pi 5 Active Cooler
5.  **ADA169** - Micro servo - SG92R (2x)
6.  **ADA373** - Breadboard-friendly 2.1mm DC barrel jack
7.  **ADA997** - Plastic Water Solenoid Valve - 12V - 1/2 Nominal
8.  **FIT0151** - DC Barrel Jack Adapter - Female
9.  **CE05279** - 5V 4 Channel Relay Module 10A
10.  **AM8936** - 12V DC 2A Fixed 2.1mm Tip Appliance Plugpack
11.  **CE04421** - Raspberry Pi Camera Board v2 - 8 Megapixels
12.  **CE06431** - Micro-HDMI to Standard HDMI 1M Cable
13.  **CE06486** - Raspberry Pi OS 32GB Preloaded uSD Card
14.  **CE07064** - Professional Solderless Breadboard BB400 - 400 tie points (Metal Backing Plate)
15.  **CE07828** - Male Pin Header 2.54mm (1x40)
16.  **DFR1015** - DC-DC Multi-output Buck Converter (3.3V/5V/9V/12V)
17.  **CE09777** - Raspberry Pi Camera FPC Adapter Cable 500mm
18.  **ADA5993** - Adafruit USB Type C Vertical Breakout - Downstream Connection (2x)

**Additional Components:**

*   Female-to-female jumpers
*   Male-to-female jumpers
*   Male-to-male jumpers
*   Jumper wires for the breadboard
*   **PCA9685** - PWM/Servo Controller to run servos without jitter

### Hardware Breakdown

*   **Power Supply:**
    *   The breadboard is powered using the 12V barrel jack adapter.
    *   A buck converter steps down 12V to 5V.  There is a 12V and 5V power rail.
    *   The Raspberry Pi is currently powered separately but I aim to power it via a 5V USB-C adapter connected to the 5V rail.  With the Pi5 you can't power it from its GPIO pins.
*   **Servos:**
    *   Two micro servos (SG92R) are connected to the PCA9685 controller to manage the pan and tilt mechanism.
    *   The PCA9685 is powered by the 5V rail and connected to the Raspberry Pi's I2C pins.
*   **Solenoid Valve:**
    *   A single channel of the 4-channel relay module controls the 12V solenoid valve.
    *   The relay module is optically isolated and directly controlled via the Raspberry Pi's GPIO pins.
*   **Camera:**
    *   The Raspberry Pi Camera Board v2 captures live video feeds for processing.
    *   Connected via the Raspberry Pi Camera FPC Adapter Cable 500mm to the PIs CSI connector
*   **Cooling and Protection:**
    *   The Raspberry Pi will be housed in an official case with an active cooler to ensure optimal performance.  The yolo image recognition burns cpu, and without a cooler the PI can thermal shutdown 

### Schematics

![Schematics](path/to/schematics.png)


Installation
------------

### Prerequisites

*   **Python 3.11.2**
*   **Virtual Environment (venv)**
*   **Git**
*   **Raspberry Pi OS** (for Raspberry Pi setup)
*   **macOS** (for Mac setup)

### Setup on Mac

1.  **Clone the Repository:**
    
        git clone https://github.com/lukerohde/watercannon.git
        cd watercannon
        
    
2.  **Run Setup Script:**
    
        ./setup-mac.sh
        
    
    This script will install all necessary dependencies and set up the virtual environment.
    

### Setup on Raspberry Pi

Do all the initial PI setup stuff, like getting on your wifi, setting up ssh etc...

1.  **Clone the Repository:**
    
        git clone https://github.com/lukerohde/watercannon.git
        cd watercannon
        
    
2.  **Run Setup Script:**
    
        ./setup-pi.sh
        
    
    This script will install all necessary dependencies, set up the virtual environment, and configure hardware-specific settings.
    
    **Note:** On first run (`yolov10n.pt`) will be downloaded
    

Running the Application
-----------------------

### Activate Virtual Environment

Before running the application, activate the virtual environment:

    source venv/bin/activate
    

### Start the App

You can start the application using one of the following methods:

1.  **Using the `go` Script:**
    
        ./go
        
    
2.  **./go just does the following **
    
        source venv/bin/active
        python start.py
        
    

### Accessing the Camera Feed

Once the application is running, you can view the live camera feed by navigating to:

    http://<ip-address-of-your-pi>:3000
    

Replace `<ip-address-of-your-pi>` with the actual IP address of your Raspberry Pi.

Testing
-------

### Automatic Test Runner

An automatic test runner monitors file changes and runs tests accordingly. To start the automatic test runner:

    ./auto_test.py
    

Ensure the virtual environment is activated before running the script.

### Manual Testing

You can manually run all unit tests using the `unittest` framework:

    python -m unittest discover
    

This command discovers and runs all tests in the `tests` directory.

Directory Structure
-------------------

    chicken-tracker/
    ├── app/
    │   ├── __init__.py
    │   ├── detector.py
    │   ├── frame_processor.py
    │   ├── frame_store.py
    │   ├── main.py
    │   └── target_tracker.py
    ├── camera/
    │   ├── __init__.py
    │   ├── base_camera.py
    │   ├── fake_camera.py
    │   ├── mac_camera.py
    │   └── pi_camera.py
    ├── hardware/
    │   ├── __init__.py
    │   ├── base_hardware.py
    │   ├── fake_hardware.py
    │   ├── mac_hardware.py
    │   ├── pi_hardware_lgpio.py
    │   └── pi_hardware_servokit.py
    ├── tests/
    │   ├── __init__.py
    │   ├── chicken_deck.jpg
    │   ├── chicken_missing.jpg
    │   ├── chickens.jpg
    │   ├── test_base_hardware.py
    │   ├── test_detector.py
    │   ├── test_frame_processor.py
    │   ├── test_main.py
    │   └── test_target_tracker.py
    ├── pi_hardware_test_lgpio.py
    ├── pi_hardware_test_servokit.py
    ├── auto_test.py
    ├── go
    ├── requirements.txt
    ├── setup-mac.sh
    ├── setup-pi.sh
    ├── start.py
    └── yolov10n.pt
    

### Module Descriptions

*   **app/**: Contains the core application logic.
    *   **main.py**: Defines the `App` class that manages the Flask server and frame processing.
    *   **frame\_store.py**: Manages thread-safe storage of the latest video frames.
    *   **detector.py**: Handles object detection in video frames.
    *   **frame\_processor.py**: Processes frames for detection and hardware control.
    *   **target\_tracker.py**: Tracks detected targets within frames.
*   **camera/**: Manages camera operations.
    *   **base\_camera.py**: Abstract base class for camera implementations.
    *   **fake\_camera.py**: Provides a fake camera for testing purposes.
    *   **mac\_camera.py**: Simulates camera interactions on Mac.
    *   **pi\_camera.py**: Interfaces with the actual Raspberry Pi camera.
*   **hardware/**: Controls hardware components.
    *   **base\_hardware.py**: Abstract base class for hardware controllers.
    *   **fake\_hardware.py**: Simulates hardware for testing.
    *   **mac\_hardware.py**: Simulates hardware interactions on Mac.
    *   **pi\_hardware\_lgpio.py**: Interfaces with hardware using GPIO on Raspberry Pi. This has jitter.
    *   **pi\_hardware\_servokit.py**: Interfaces with hardware using the ServoKit on Raspberry Pi for the PCA9685 for no jitter - totally worth the extra $15
*   **tests/**: Contains all unit tests and test resources.
    *   **test\_base\_hardware.py**: Tests the base hardware controller.
    *   **test\_detector.py**: Tests the object detection logic.
    *   **test\_frame\_processor.py**: Tests the frame processing functionality.
    *   **test\_main.py**: Tests the main application logic.
    *   **test\_target\_tracker.py**: Tests the target tracking functionality.
    *   **chicken\_deck.jpg**, **chicken\_missing.jpg**, **chickens.jpg**: Test images for detection and tracking.
*   **pi\_hardware\_test\_lgpio.py**: For manually testing your servo and relay hardware using LGPIO lib.  None of the other GPIO methods work well on PI5.
*   **pi\_hardware\_test\_servokit.py**: For manually testing your servo and relay hardware using using ServoKit.
*   **auto\_test.py**: Automatic test runner that watches for file changes.
*   **go**: Convenience script to start the application.
*   **requirements.txt**: Python dependencies.
*   **setup-mac.sh**: Shell script to set up the environment on Mac.
*   **setup-pi.sh**: Shell script to set up the environment on Raspberry Pi.
*   **start.py**: Entry point to run the application.
*   **yolov10n.pt**: YOLOv10n model file downloaded by the YOLO library during first run.

How It Works
------------

1.  **Frame Processing:**
    *   The application initializes a camera (real or fake) and starts a background thread to continuously process video frames.
    *   Each frame is passed through the `FrameProcessor`, which uses the `Detector` to identify chickens.
    *   Detected chickens are tracked using the `TargetTracker`, and corresponding signals are sent to the `HardwareController` to move pan and tilt servos and activate the solenoid valve.
2.  **Frame Store:**
    *   Processed frames are stored in a thread-safe `FrameStore`, ensuring that the latest frame is always available for streaming.
    *   The `FrameStore` uses locks and condition variables to manage concurrent access from the processing thread and Flask's streaming routes.
3.  **Flask Streaming:**
    *   The Flask web server runs concurrently, streaming the latest frames from the `FrameStore` to any connected clients.
    *   Clients can access the live feed by navigating to `http://<ip-address-of-your-pi>:3000` in a web browser.
4.  **Hardware Control:**
    *   The `HardwareController` manages servos for the pan and tilt mechanism and controls the solenoid valve via GPIO pins.
    *   On detection of a chicken, the system automatically adjusts the servos to target the chicken and activates the solenoid to spray water.

Contribution
------------

Contributions are welcome! Please follow these guidelines:

1.  **Fork the Repository:** Click the "Fork" button at the top of the repository page to create a personal copy.
2.  **Create a Feature Branch:**
    
        git checkout -b feature/YourFeatureName
        
        PLEASE INCLUDE TESTS!

3.  **Commit Your Changes:**
    
        git commit -m "Add your message here"
        
    
4.  **Push to Your Fork:**
    
        git push origin feature/YourFeatureName
        
    
5.  **Open a Pull Request:** Navigate to the original repository and click "New Pull Request."

**Note:** All contributions must include passing unit tests. Please ensure that your code adheres to the existing style and conventions.

License
-------

This project is licensed under the [MIT License](LICENSE).

Shout-Outs
----------

To the PI, OSS and maker communities - you are amazing.  This stuff is cool and cheap, and your online knowledge is priceless.  

YoloV10 is pretty awesome too. It runs a reasonable 1 FPS on the PI CPU!

Plus a big shoutout to OpenAI's [O1 Mini](https://openai.com/index/openai-o1-mini-advancing-cost-efficient-reasoning/)  for teaching me electronics and making this a few nights project.  

O1 Mini writes error free code!  It wrote that autotest.py magic in one go - faster than I could google 'python version of rails guard::minitest'.  It taught me simple ways to stream video. It handled the async, thread safe decoupling of video-streaming and video-processing with grace.  Async programming plus me and AI is normally a disasterous recipe of the blind leading the blind.

To build it, I went unit test by unit test, in a TDD kind of way, coaxing O1 Mini to refactor for testability and making sure I understood the code as we went.  I hit play and it just worked!  This was shocking.  

Disclaimer
----------

**WaterCannon** is a hobby project and is not thoroughly tested on hardware configurations other than those specified. Use at your own risk. The author is not liable for any damages, animal harm or false spraying arising from the use of this project.

* * *

For any questions, please contact luke rohde at gmail - I don't really read my email, so ¯\\\_(ツ)\_/¯