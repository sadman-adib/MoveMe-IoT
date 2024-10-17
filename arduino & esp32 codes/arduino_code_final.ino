/// ARDUINO FINAL CODE

#include <Wire.h>                        // For I2C communication
#include <Adafruit_GFX.h>                // Graphics library for OLED
#include <Adafruit_SSD1306.h>            // OLED display driver
#include <RTClib.h>                      // Library for RTC

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1                 // Reset pin (not used)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

RTC_DS3231 rtc;                          // Initialize RTC (use RTC_DS1307 if using DS1307)

String lastReceivedData = "";            // Variable to store the last received data
DateTime lastUpdateTime;                 // Stores the last time we received data
int availableSeats = -1;                 // Variable to store available seats
bool dataReceived = false;               // Flag to indicate new data

// Timing variables
unsigned long lastOLEDUpdateMillis = 0;

const long oledUpdateInterval = 500;    // 1 second for updating the OLED

void setup() {
  // Initialize Serial communication with Serial Monitor
  Serial.begin(115200);
  Serial1.begin(115200);  // Communication between ESP32 and ESP-01 (connected via Serial1-18/19)

  // Initialize the OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Stay in a loop if allocation failed
  }

  // Initialize RTC
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1); // Stay in a loop if RTC initialization failed
  }

  // Always reset the RTC time to the current system time (compile time)
  resetRTCToSystemTime();

  // Clear the buffer and display a message on the OLED
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Waiting for data...");
  display.display();

  // Start ESP-01 as a server on port 3300
  sendCommand("AT+CWMODE=1", 2000);  // Set to station mode
  sendCommand("AT+CWJAP=\"Galaxy M3113FF\",\"wajq2142\"", 10000);  // Connect to Wi-Fi
  sendCommand("AT+CIPSTA=\"192.168.224.110\",\"192.168.224.109\",\"255.255.255.0\"", 2000); // Set static IP
  sendCommand("AT+CIPMUX=1", 1000);  // Enable multiple connections
  sendCommand("AT+CIPSERVER=1,3300", 2000);  // Start server on port 3300

  Serial.println("ESP-01 Server started, waiting for data...");
}

void loop() {
  unsigned long currentMillis = millis();

  // Check for incoming Wi-Fi data continuously
  if (Serial1.available()) {
    checkForIncomingData();  // Check for incoming data from ESP-01
  }

  // Update the OLED display every 1 second
  if (currentMillis - lastOLEDUpdateMillis >= oledUpdateInterval) {
    lastOLEDUpdateMillis = currentMillis;
    updateOLEDDisplay();  // Update OLED display with current time, available seats, etc.
  }
}

// Function to check for incoming data from ESP-01
void checkForIncomingData() {
  if (Serial1.available()) {
    String response = Serial1.readString();  // Read the incoming request
    Serial.println("Data received from client:");
    Serial.println(response);  // Print the received data

    // If response contains +IPD (indicating incoming data from ESP-01)
    if (response.indexOf("+IPD") != -1) {
      // Strip the +IPD,0,90: part to get the actual data
      int dataStartIndex = response.indexOf("{");
      if (dataStartIndex != -1) {
        String jsonData = response.substring(dataStartIndex); // Extract the JSON part
        Serial.println("Extracted Data: " + jsonData);
        
        // Parse the JSON-like string manually to extract 'available_slots'
        availableSeats = parseAvailableSeats(jsonData);
        lastUpdateTime = rtc.now();  // Record the time we received this data
        dataReceived = true;  // Mark that we received new data
      }
    }
  }
}

// Function to update the OLED display with current time, available seats, and last updated info
void updateOLEDDisplay() {
  DateTime now = rtc.now();
  String timeNow = String(now.hour()) + ":" + String(now.minute()); // Only Hour and Min
  String lastUpdated = calculateTimeDifference(lastUpdateTime, now);  // Calculate time difference

  // Update the OLED display with the current time, available seats, and last updated
  display.clearDisplay();
  
  display.setCursor(0, 0);
  display.print("Current Time: ");
  display.print(timeNow);  // Only show hour and minute

  display.setCursor(0, 15);
  display.print("Available Seats: ");
  display.print(availableSeats);  // Show available seats

  display.setCursor(0, 30);
  display.print("Last Updated: ");
  display.print(lastUpdated);  // Time since last update

  display.display();  // Show the updated information
}

// Function to reset the RTC time to the current system time (at compile time)
void resetRTCToSystemTime() {
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));  // Set RTC time to system's current time at compile time
  Serial.println("RTC time has been reset to system time.");
}

// Function to parse 'available_slots' from the incoming data string
int parseAvailableSeats(String jsonData) {
  int availableSeats = -1;
  int availableSeatsIndex = jsonData.indexOf("'available_slots': ");
  
  if (availableSeatsIndex != -1) {
    availableSeatsIndex += strlen("'available_slots': ");
    String seatsValue = jsonData.substring(availableSeatsIndex, jsonData.indexOf(",", availableSeatsIndex));
    availableSeats = seatsValue.toInt();
  }
  
  return availableSeats;
}

// Function to calculate the difference in time between when data was received and now
String calculateTimeDifference(DateTime lastTime, DateTime currentTime) {
  TimeSpan timeDiff = currentTime - lastTime;  // Calculate the difference
  return String(timeDiff.hours()) + "h " + String(timeDiff.minutes()) + "m " + String(timeDiff.seconds()) + "s";
}

// Function to send AT commands to the ESP-01 and wait for a response
void sendCommand(const char* command, int timeout) {
  Serial1.println(command);  // Send the command to ESP-01
  long int time = millis();
  while ((time + timeout) > millis()) {
    while (Serial1.available()) {
      char c = Serial1.read();
      Serial.write(c);  // Print the response to the Serial Monitor
    }
  }
}
