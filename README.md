<h1 align="center">MoveMe – An Energy-Efficient Smart Bus Transport Management System with Blind-Spot Collision Detection Ability</h1>

<p align="center"><strong>IoT-powered, AI-driven, and solar-powered solution for safe, efficient, and sustainable public transport in developing countries.</strong></p>

---

## Overview
<strong>MoveMe</strong> integrates multiple smart features to improve safety, efficiency, and sustainability in public transport:

- Real-time bus tracking  
- Blind-spot collision detection (YOLOv4-Tiny + Raspberry Pi)  
- Automated bus-stop detection  
- RFID-based passenger counting  
- Smart bus-door control with safety override  
- Solar-powered smart bus stops  

---

## Motivation
Public transport in developing countries faces challenges such as unreliable schedules, congestion, and safety risks. MoveMe solves these by:

- Providing real-time location to passengers  
- Using AI-based blind-spot detection to prevent accidents  
- Reducing carbon footprint via solar power  
- Offering analytics for better transport management  

---

## System Architecture
**Core Features**
1. **Blind-Spot Collision Detection** – YOLOv4-Tiny on Raspberry Pi with ultrasonic sensor & buzzer  
2. **Smart Bus-Stop Detection** – Alerts driver at designated stops  
3. **RFID Passenger Counting** – Tracks boarding/exiting in real time  
4. **Smart Bus-Door Control** – Stepper motor with emergency override  
5. **Real-Time Bus Tracking** – GPS + cloud updates  
6. **Solar-Powered Smart Stops** – 10W panel + 12V 5Ah battery  

---

## Repository Structure
MoveMe/
  1. raspberry_pi_codes/
    a. object_detection.py
    b. rfid_test.py
  2. arduino_esp32_codes/
    a. arduino_code_final.ino
    b. esp32_code_final.ino

---

## Code Breakdown
**`raspberry_pi_codes`**
- `object_detection.py` – Runs YOLOv4-Tiny for blind-spot & bus-stop detection, controls alerts, sensors, and smart door motor.  
- `rfid_test.py` – Reads RFID cards, tracks passenger count, sends data via TCP to ESP32 & bus stop servers.  

**`arduino_esp32_codes`**
- `arduino_code_final.ino` – Displays seats, time, and updates on OLED; syncs with ESP32 for bus stop updates.  
- `esp32_code_final.ino` – Receives passenger data from Raspberry Pi, uploads to cloud (PHP/MySQL), and serves local TCP clients.  

---

## Hardware Requirements
- Raspberry Pi 4B (4GB)  
- ESP32 & Arduino Mega  
- ESP-01 WiFi module  
- RFID reader  
- Stepper motor + driver  
- Ultrasonic sensor  
- Buzzer & LED  
- GPS module  
- 0.96" I2C OLED display  
- 10W Solar panel + 12V 5Ah battery  

---

## Software Requirements
- Python 3 (OpenCV, NumPy, RPi.GPIO)  
- YOLOv4-Tiny weights & config  
- Arduino IDE (Adafruit_GFX, Adafruit_SSD1306, RTClib)  
- ESP32 Arduino core + ArduinoJson  

---

## Contributors
- **Md. Sadman Haque** – Research Lead  
- Zobaer Ibn Razzaque  
- Robiul Awoul Robin  

---

