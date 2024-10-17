import threading
import socket
import time
import csv
import os
from collections import deque

class RFIDSystem:
    def __init__(self, total_slots=40, reconnect_delay=5, csv_file="rfid_log.csv"):
        self.total_slots = total_slots
        self.available_slots = total_slots
        self.passengers = {}
        self.passenger_id_queue = deque()  # Queue to store passenger IDs
        self.reconnect_delay = reconnect_delay
        self.csv_file = csv_file
        self.data_queue = deque()
        self.bus_stops_queue = deque()

        self.data_server_socket = None
        self.bus_stops_server_socket = None

        self.data_server = ('192.168.224.207', 3300)
        self.bus_stops_server = ('192.168.224.110', 3300)

        self.load_from_csv()

        threading.Thread(target=self.connect_servers, daemon=True).start()

    def load_from_csv(self):
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'RFID' in row:
                        self.passengers[row['RFID']] = True
                        self.available_slots = int(row['Available Seats'])
            print(f"Loaded {len(self.passengers)} passengers from previous session.")

    def save_to_csv(self):
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Timestamp", "Total Passengers", "Available Seats", "RFID"])
            writer.writeheader()

            for rfid in self.passengers:
                writer.writerow({
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Total Passengers": len(self.passengers),
                    "Available Seats": self.available_slots,
                    "RFID": rfid
                })

    def punch_rfid(self, rfid):
        if rfid not in self.passengers:
            self.passengers[rfid] = True
            self.available_slots -= 1
            self.passenger_id_queue.append(rfid)  # Add to passenger ID queue
        else:
            del self.passengers[rfid]
            self.available_slots += 1
            # Check if the RFID is in the queue before removing it
            if rfid in self.passenger_id_queue:
                self.passenger_id_queue.remove(rfid)  # Remove from passenger ID queue

        self.display_status()
        self.save_to_csv() 
        self.send_status()  # Send the updated status to servers

    def display_status(self):
        total_passengers = len(self.passengers)
        print(f"Total passengers: {total_passengers}")
        print(f"Available seats: {self.available_slots}\n")

    def get_status(self):
        return {
            "total_passengers": len(self.passengers),
            "available_slots": self.available_slots,
            "passengers": list(self.passengers.keys())
        }

    def queue_status(self, status_str, server_type):
        if server_type == 'data':
            self.data_queue.append(status_str)
        elif server_type == 'bus_stops':
            self.bus_stops_queue.append(status_str)

    def send_queued_data(self):
        while self.data_queue:
            status_str = self.data_queue.popleft() + '\n'  # Add newline character
            if self.data_server_socket:
                try:
                    self.data_server_socket.sendall(status_str.encode())
                    print(f"Sent to Data Server: {status_str.strip()}")  # Use strip() to remove the newline for printing
                except socket.error:
                    print("Failed to send queued data to Data Server, re-queueing.")
                    self.queue_status(status_str.strip(), 'data')  # Use strip() to remove the newline for re-queueing
                    break

        while self.bus_stops_queue:
            status_str = self.bus_stops_queue.popleft() + '\n'  # Add newline character
            if self.bus_stops_server_socket:
                try:
                    self.bus_stops_server_socket.sendall(status_str.encode())
                    print(f"Sent to Bus Stops Server: {status_str.strip()}")  # Use strip() to remove the newline for printing
                except socket.error:
                    print("Failed to send queued data to Bus Stops Server, re-queueing.")
                    self.queue_status(status_str.strip(), 'bus_stops')  # Use strip() to remove the newline for re-queueing
                    break

    def send_status(self):
        # If available slots are 40, set total passengers to 0
        if self.available_slots == self.total_slots:
            total_passengers = 0
            passengers = [-1]  # When no passengers, set passenger IDs to -1
        else:
            total_passengers = len(self.passengers)
            passengers = list(self.passengers.keys())

        status = {
            "total_passengers": total_passengers,
            "available_slots": self.available_slots,
            "passengers": passengers
        }
        status_str = str(status) + '\n'  # Add newline character

        # Send status to Data Server if connected, or queue the data
        if self.data_server_socket:
            try:
                self.data_server_socket.sendall(status_str.encode())
                print(f"Sent to Data Server: {status_str.strip()}")  # Optional print statement
            except socket.error:
                print("Disconnected from Data Server, queuing data...")
                self.queue_status(status_str.strip(), 'data')  # Use strip() to remove the newline for re-queueing
                self.data_server_socket = None
        else:
            self.queue_status(status_str.strip(), 'data')

        # Create a simplified status string for the bus stops server
        bus_stops_status = {
            "total_passengers": total_passengers,
            "available_slots": self.available_slots,
            "passengers": passengers
        }
        bus_stops_status_str = str(bus_stops_status) + '\n'  # Add newline character

        # Send status to Bus Stops Server if connected, or queue the data
        if self.bus_stops_server_socket:
            try:
                self.bus_stops_server_socket.sendall(bus_stops_status_str.encode())
                print(f"Sent to Bus Stops Server: {bus_stops_status_str.strip()}")  # Optional print statement
            except socket.error:
                print("Disconnected from Bus Stops Server, queuing data...")
                self.queue_status(bus_stops_status_str.strip(), 'bus_stops')  # Use strip() to remove the newline for re-queueing
                self.bus_stops_server_socket = None
        else:
            self.queue_status(bus_stops_status_str.strip(), 'bus_stops')

    def connect_servers(self):
        while True:
            try:
                if self.data_server_socket is None:
                    self.connect_data_server()

                if self.bus_stops_server_socket is None:
                    self.connect_bus_stops_server()

                if self.data_server_socket or self.bus_stops_server_socket:
                    self.send_queued_data()

            except socket.error as e:
                print(f"Connection failed: {e}. Retrying in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

            time.sleep(1)  # Check connection status periodically

    def connect_data_server(self):
        try:
            print("Attempting to connect to Data Server...")
            self.data_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_server_socket.connect(self.data_server)
            print("Connected to Data Server")
        except socket.error as e:
            print(f"Failed to connect to Data Server: {e}.")
            self.data_server_socket = None

    def connect_bus_stops_server(self):
        try:
            print("Attempting to connect to Bus Stops Server...")
            self.bus_stops_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bus_stops_server_socket.connect(self.bus_stops_server)
            print("Connected to Bus Stops Server")
        except socket.error as e:
            print(f"Failed to connect to Bus Stops Server: {e}.")
            self.bus_stops_server_socket = None

    def close_connections(self):
        print("Closing connections...")
        if self.data_server_socket:
            self.data_server_socket.close()
        if self.bus_stops_server_socket:
            self.bus_stops_server_socket.close()

# Initialize the RFID system
rfid_system = RFIDSystem()

def is_valid_rfid(input_str):
    """
    Check if the input string looks like a valid RFID number.
    Here, assuming a valid RFID is purely numeric and has a reasonable length (e.g., 8-10 digits).
    Modify this logic as per actual RFID format.
    """
    return input_str.isdigit() and 8 <= len(input_str) <= 10

try:
    while True:
        print("\nRFID System is ready. Please scan an RFID card.")
        
        rfid = input("Scan RFID card (or type 'exit' to stop): ").strip()

        # Debugging output
        print(f"RFID input captured: {rfid}")

        # Extract RFID if path is captured
        if rfid.startswith('/'):
            rfid = os.path.basename(rfid.split()[-1])
            print(f"Extracted RFID: {rfid}")

        # Validate that the extracted RFID looks like an actual RFID number
        if is_valid_rfid(rfid):
            print(f"Valid RFID detected: {rfid}")
            rfid_system.punch_rfid(rfid)
        else:
            print(f"Invalid RFID or command: {rfid}")

        if rfid.lower() == 'exit':
            break

except KeyboardInterrupt:
    print("Shutting down RFID system...")
    rfid_system.close_connections()
