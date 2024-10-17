import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime
import threading

# Setup GPIO for LED, Button, Stepper Motor, Ultrasonic Sensor, and Buzzer
LED_PIN = 27
BUTTON_PIN = 17
IN1_PIN = 6
IN2_PIN = 13
IN3_PIN = 16
IN4_PIN = 26
TRIG = 23
ECHO = 24
BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)
GPIO.setup(IN3_PIN, GPIO.OUT)
GPIO.setup(IN4_PIN, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Stepper motor step sequence (half-step mode)
step_sequence = [
    [1, 0, 0, 1],  # Step 1
    [1, 0, 0, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [0, 1, 0, 0],  # Step 4
    [0, 1, 1, 0],  # Step 5
    [0, 0, 1, 0],  # Step 6
    [0, 0, 1, 1],  # Step 7
    [0, 0, 0, 1]   # Step 8
]

# Load YOLO
net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")

# Specify the classes you're interested in for the buzzer
required_classes = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", 
                    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", 
                    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", 
                    "giraffe", "sports ball"]

# Load class labels
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize the camera
cap = cv2.VideoCapture(0)

# Button press counter and stepper motor position flag
press_count = 0
door_open = False

# CSV file for logging
csv_file = "door_log.csv"

# Function to write to CSV file
def log_event(event):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        now = datetime.now()
        writer.writerow([event, now.strftime("%Y-%m-%d %H:%M:%S")])

# Function to move stepper motor forward or backward
def move_stepper(steps, direction):
    for _ in range(steps):
        for step in range(8):
            for pin in range(4):
                GPIO.output([IN1_PIN, IN2_PIN, IN3_PIN, IN4_PIN][pin], step_sequence[step][pin] if direction == "forward" else step_sequence[7-step][pin])
            time.sleep(0.002)  # Adjust this delay for speed

# Door open (forward) and close (backward) movement control
def open_door():
    move_stepper(128, "forward")  # 512 steps for a full 90-degree rotation (adjust as needed)
    log_event("open the door")
    print("1st press (open the door)")

def close_door():
    move_stepper(128, "backward")
    print("2nd press (close the door)")

def emergency_open_door():
    move_stepper(128, "forward")
    log_event("emergency open the door")
    print("1st press (emergency open the door)")

def emergency_close_door():
    move_stepper(128, "backward")
    print("2nd press (emergency close the door)")

def measure_distance():
    # Trigger the sensor
    GPIO.output(TRIG, False)
    time.sleep(0.5)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # Measure pulse duration
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# Function to detect objects and handle the buzzer
def detect_objects_and_buzzer():
    global press_count, door_open
    fps = 0
    frame_count = 0
    start_time = time.time()

    # Load YOLO output layers
    layer_names = net.getLayerNames()
    output_layers_indices = net.getUnconnectedOutLayers()
    output_layers = [layer_names[i - 1] for i in output_layers_indices.flatten()]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Prepare the frame for YOLO
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
        net.setInput(blob)

        # Run forward pass and get output
        outs = net.forward(output_layers)

        # Process the outputs
        class_ids = []
        confidences = []
        boxes = []
        stop_sign_detected = False

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.3:  # Confidence threshold for faster results
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply Non-max suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Handle empty `indexes` case
        if isinstance(indexes, tuple) and len(indexes) == 0:
            indexes = np.array([])

        if len(indexes) > 0:
            indexes = indexes.flatten()

        # Check for stop sign and control LED
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                if label == "stop sign":  # Check if the detected object is a stop sign
                    stop_sign_detected = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a green rectangle
                    cv2.putText(frame, "bus stop", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)  # Label above the rectangle

                if label in required_classes:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a green rectangle
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)  # Label above the rectangle
    

        # Control LED based on detection of stop sign
        if stop_sign_detected:
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on LED
        else:
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn off LED

        # Measure distance and control buzzer for required classes
        object_detected = len(indexes) > 0
        
        if object_detected:
            distance = measure_distance()
            print(f'Distance to detected object: {distance} cm')

            # Check distance and control buzzer for required classes
            for i in indexes.flatten():
                if i < len(class_ids):
                    label = str(classes[class_ids[i]])
                    if label in required_classes:
                        if distance < 200:  # Distance in cm (2 meters)
                            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on buzzer
                            print("Buzzer ON")
                        else:
                            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off buzzer
                            print("Buzzer OFF")
                    # If distance is less than 200 cm, mark as blind spot
                    if distance < 200:
                        cv2.rectangle(frame, boxes[i][:2], (boxes[i][0] + boxes[i][2], boxes[i][1] + boxes[i][3]), (0, 0, 255), 2)  # Red box
                        cv2.putText(frame, "blind-spot", (boxes[i][0], boxes[i][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off buzzer if no objects detected

        # Calculate FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        # Display FPS
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Show the frame with detections
        cv2.imshow("Object Detection", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# Thread to detect objects and manage the buzzer
t1 = threading.Thread(target=detect_objects_and_buzzer)
t1.start()

try:
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == GPIO.LOW:  # Button is pressed
            press_count += 1
            if press_count == 1:
                open_door()
            elif press_count == 2:
                close_door()
                press_count = 0

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()

