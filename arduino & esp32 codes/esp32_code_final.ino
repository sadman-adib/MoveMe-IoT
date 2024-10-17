// ESP-32 FINAL

#include <WiFi.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "Galaxy M3113FF";
const char* password = "wajq2142";

// Server URL to upload data
const char* serverName = "http://192.168.224.218/upload_data.php";

// Local TCP server (ESP32 will act as a server to receive data)
WiFiServer tcpServer(3300);   // ESP32 will listen for incoming data on port 3300

String receivedData = "";  // Buffer to hold the received data
bool isDataComplete = false;  // Flag to determine if full data has been received

// Function to send URL-encoded data to the PHP server
void sendToServer(int total_passengers, int available_slots, String passenger) {
  if (WiFi.status() == WL_CONNECTED) {  // Check Wi-Fi connection status
    HTTPClient http;  // Create HTTP client object

    // Format the data as URL-encoded
    String postData = "total_passengers=" + String(total_passengers) +
                      "&available_slots=" + String(available_slots) +
                      "&passenger=" + passenger;

    Serial.println("Sending the following form data:");
    Serial.println(postData);

    // Start the connection to the PHP server
    http.begin(serverName);  // Specify the URL to the PHP script
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");  // Specify that we are sending form data

    // Send the HTTP POST request
    int httpResponseCode = http.POST(postData);

    // Check the response code and print result
    if (httpResponseCode > 0) {
      String response = http.getString();  // Get the response from the server
      Serial.println(httpResponseCode);    // Print return code (200 is successful)
      Serial.println(response);            // Print the response from the server
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);    // Print the error code if there was an error
      Serial.println(http.errorToString(httpResponseCode));  // Print the error string
    }

    http.end();  // Free resources
  } else {
    Serial.println("Error in WiFi connection");
  }
}

void setup() {
  Serial.begin(115200);
  connectToWiFi();

  // Start the local TCP server to listen for incoming data
  tcpServer.begin();
  Serial.println("TCP server started, waiting for client connections...");
}

void loop() {
  // Check if a client has connected to the local TCP server
  WiFiClient client = tcpServer.available();

  if (client) {
    Serial.println("Client connected.");
    unsigned long timeoutStart = millis();  // Start a timeout counter

    // Keep reading data sent by the client
    while (client.connected()) {
      while (client.available()) {  // While data is available
        char c = client.read();   // Read one byte at a time
        receivedData += c;

        // Print received byte for debugging
        Serial.print(c);  // Print each received character immediately

        // If we detect a closing brace '}', assume the message is complete
        if (c == '}') {
          isDataComplete = true;
          break;  // Exit the reading loop
        }
      }

      // Break out of the loop if full data is received
      if (isDataComplete) {
        break;
      }

      // Timeout if no data is received within 5 seconds
      if (millis() - timeoutStart > 5000) {
        Serial.println("Timeout: No data received for 5 seconds.");
        receivedData = "";  // Clear the buffer in case of timeout
        isDataComplete = false;
        break;
      }
    }

    // If full data was received, process it
    if (isDataComplete) {
      Serial.println("\nFull data received from client:");
      Serial.println(receivedData);  // Print full data received

      // Process the received JSON data and extract values
      processAndUploadData(receivedData);

      // Clear the received data buffer for the next message
      receivedData = "";
      isDataComplete = false;  // Reset the flag for next time
    }
  }
}

// Function to process the received data and send it to the server
void processAndUploadData(String data) {
  // Example JSON data received:
  // {"total_passengers": 2, "available_slots": 38, "passengers": ["0002661202", "0003613527"]}
  
  // Deserialize the JSON data
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, data);

  if (error) {
    Serial.print("Failed to parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Extract values from the JSON
  int total_passengers = doc["total_passengers"];
  int available_slots = doc["available_slots"];
  JsonArray passengersArray = doc["passengers"];  // Get the passengers array

  // Loop through the passengers array in reverse order
  for (int i = passengersArray.size() - 1; i >= 0; i--) {
    String passenger = passengersArray[i].as<String>();  // Get each passenger

    // Decrement total_passengers and increment available_slots
    int current_passengers = total_passengers - (passengersArray.size() - i - 1);
    int current_slots = available_slots + (passengersArray.size() - i - 1);

    // Print the decoded values before sending to the server
    Serial.println("Decoded JSON:");
    Serial.print("Total Passengers: ");
    Serial.println(current_passengers);
    Serial.print("Available Slots: ");
    Serial.println(current_slots);
    Serial.print("Passenger: ");
    Serial.println(passenger);

    // Send the extracted data to the remote server
    sendToServer(current_passengers, current_slots, passenger);
  }
}

// Function to handle Wi-Fi connection
void connectToWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  // Wait for Wi-Fi connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); // Wait 1 second between attempts
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal Strength (RSSI): ");
  Serial.println(WiFi.RSSI());  // Print Wi-Fi signal strength
}
