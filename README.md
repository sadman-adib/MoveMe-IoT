<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoveMe – Smart Bus Transport System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            background-color: #f9f9f9;
            color: #333;
        }
        h1, h2, h3 {
            color: #005f73;
        }
        code {
            background-color: #eee;
            padding: 2px 5px;
            border-radius: 4px;
            font-family: monospace;
        }
        pre {
            background-color: #eee;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .highlight {
            background-color: #e0f7fa;
            padding: 4px;
            border-radius: 4px;
        }
        ul {
            margin-left: 20px;
        }
        .section {
            background: white;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>

    <h1>MoveMe – An Energy-Efficient Smart Bus Transport Management System with Blind-Spot Collision Detection Ability</h1>

    <div class="section">
        <h2> Overview</h2>
        <p><strong>MoveMe</strong> is an <strong>IoT-powered</strong>, <strong>energy-efficient</strong> public transport management system designed to improve <strong>safety, efficiency, and sustainability</strong> in developing countries.</p>
        <p>The system integrates:</p>
        <ul>
            <li>Real-time bus tracking</li>
            <li>Blind-spot collision detection</li>
            <li>Automated bus-stop detection</li>
            <li>RFID-based passenger counting</li>
            <li>Smart bus-door control</li>
            <li>Solar-powered smart bus stops</li>
        </ul>
    </div>

    <div class="section">
        <h2>Motivation</h2>
        <p>Public transport in developing countries often suffers from <strong>unreliable schedules</strong>, <strong>traffic congestion</strong>, and <strong>safety concerns</strong>. MoveMe addresses these issues by:</p>
        <ul>
            <li>Providing live location updates for passengers</li>
            <li>Enhancing road safety with deep learning blind-spot detection</li>
            <li>Reducing environmental impact with solar-powered stops</li>
            <li>Enabling passenger data analytics for better transport management</li>
        </ul>
    </div>

    <div class="section">
        <h2>System Architecture</h2>
        <h3>Core Features</h3>
        <ol>
            <li><strong>Blind-Spot Collision Detection</strong> – YOLOv4-Tiny on Raspberry Pi with ultrasonic sensor and buzzer</li>
            <li><strong>Smart Bus-Stop Detection</strong> – Detects designated stops and alerts the driver</li>
            <li><strong>RFID-Based Passenger Counting</strong> – Tracks boarding/exiting in real time</li>
            <li><strong>Smart Bus-Door Control</strong> – Stepper motor with emergency override</li>
            <li><strong>Real-Time Bus Tracking</strong> – GPS updates to passengers and bus stops</li>
            <li><strong>Solar-Powered Smart Stops</strong> – 10W panel + 12V 5Ah battery for sustainable power</li>
        </ol>
    </div>

    <div class="section">
        <h2>📂 Repository Structure</h2>
        <pre>
📁 MoveMe
│
├── 📁 raspberry_pi_codes
│   ├── object_detection.py
│   ├── rfid_test.py
│
├── 📁 arduino_esp32_codes
│   ├── arduino_code_final.ino
│   ├── esp32_code_final.ino
│
└── README.md
        </pre>
    </div>
        <div class="section">
        <h2>Code Breakdown</h2>
        <h3>📁 raspberry_pi_codes</h3>
        <ul>
            <li><code>object_detection.py</code> – Runs YOLOv4-Tiny object detection for blind-spot & bus-stop detection, controls LED alerts, buzzer, ultrasonic sensor, and stepper motor for smart bus-door operation.</li>
            <li><code>rfid_test.py</code> – Handles RFID card reading for passenger boarding/exiting, maintains seat availability, and sends passenger data to ESP32 & bus stop servers over TCP.</li>
        </ul>
        <h3>📁 arduino_esp32_codes</h3>
        <ul>
            <li><code>arduino_code_final.ino</code> – Displays available seats, time, and last update info on OLED; receives passenger data from ESP32 (via ESP-01) and runs a local TCP server for bus stop display updates.</li>
            <li><code>esp32_code_final.ino</code> – Receives passenger data from Raspberry Pi, processes it, and uploads to a remote PHP/MySQL server via HTTP; also acts as TCP server for local communication.</li>
        </ul>
    </div>

    <div class="section">
        <h2>Hardware Requirements</h2>
        <ul>
            <li>Raspberry Pi 4B (4GB)</li>
            <li>ESP32 & Arduino Mega</li>
            <li>ESP-01 WiFi module</li>
            <li>RFID reader</li>
            <li>Stepper motor + driver</li>
            <li>Ultrasonic sensor</li>
            <li>Buzzer & LED</li>
            <li>GPS module</li>
            <li>0.96" I2C OLED display</li>
            <li>10W Solar panel + 12V 5Ah battery</li>
        </ul>
    </div>

    <div class="section">
        <h2>Software Requirements</h2>
        <ul>
            <li>Python 3 (OpenCV, NumPy, RPi.GPIO)</li>
            <li>YOLOv4-Tiny weights & config</li>
            <li>Arduino IDE (Adafruit_GFX, Adafruit_SSD1306, RTClib)</li>
            <li>ESP32 Arduino core + ArduinoJson</li>
        </ul>
    </div>

    <div class="section">
        <h2>Contributors</h2>
        <ul>
            <li><strong>Md. Sadman Haque</strong> – Research Lead</li>
            <li>Zobaer Ibn Razzaque</li>
            <li>Robiul Awoul Robin</li>
        </ul>
    </div>

</body>
</html>

