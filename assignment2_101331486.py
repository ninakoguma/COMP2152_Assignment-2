"""
Author: Vienna Prudenciano
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime

import socket
import threading
import sqlite3
import os
import platform
import datetime

# TODO: Print Python version and OS name (Step iii)
print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {os.name}")

# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores

# dictionary maps common port numbers to their associated network service names
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"

class NetworkTool:
    def __init__(self, target):
        self.__target = target

# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)

# Using @property and @target.setter allows encapsulation, protecting internal data from invalid states.
# This approach allows for the implementation of validation logic, like checking for empty strings, 
# without changing how users interact with the attribute. 
# As a result to this, the interface remains clean while we maintain control over the data.

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value.strip() == "":
            print("Error: The target cannot be empty")
        else:
            self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")

# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# The PortScanner inherits from NetworkTool to access the logic for the 'target' property.
# By calling super().init(target), it will leverage the parent class's initialization
# and validation code instead of rewriting it.

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()

def scan_port(self, port):

# Q4: What would happen without try-except here?
# TODO: Your 2-4 sentence answer here... (Part 2, Q4)
# Without a try-except block, any network-level error, such as a timeout or an unreachable host,
# could cause the specific thread or the entire program to crash. 
# This would stop the loop's execution, preventing the user from receiving the final scan report.

#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((self.target, port))
            
        status = "Open" if result == 0 else "Closed"
        service_name = common_ports.get(port, "Unknown")

        with self.lock:
            self.scan_results.append((port, status, service_name))
        
    except socket.error as e:
            print(f"Error in scanning port {port}: {e}")
    finally:
            sock.close()

# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results

def get_open_ports(self):
        return [res for res in self.scan_results if res[1] == "Open"]

# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)

# Q2: Why do we use threading instead of scanning one port at a time?
# TODO: Your 2-4 sentence answer here... (Part 2, Q2)
# Scanning ports sequentially is slow, as the timeout for each port accumulates; 
# for instance, scanning 100 ports with a 1-second timeout could take 100 seconds. 
# By using threading, we can check multiple ports simultaneously, 
# significantly reducing the total scan time to roughly the duration of a single timeout.

def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()

# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )""")
        
        for port, status, service in results:
            cursor.execute("""INSERT INTO scans (target, port, status, service, scan_date) 
                           VALUES (?, ?, ?, ?, ?)""", 
                           (target, port, status, service, str(datetime.datetime.now())))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection

def load_past_scans():
    if not os.path.exists("scan_history.db"):
        print("No past scans can be found.")
        return

    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT scan_date, target, port, service, status FROM scans")
        rows = cursor.fetchall()
        
        if not rows:
            print("No past scans can be found.")
        else:
            for row in rows:
                print(f"[{row[0]}] {row[1]} : Port {row[2]} ({row[3]}) - {row[4]}")
        conn.close()
    except sqlite3.Error:
        print("No past scans can be found.")

# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
    
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."

        target_ip = input("Enter target IP (default 127.0.0.1): ") or "127.0.0.1"
        start_p = int(input("Enter start port (1-1024): "))
        end_p = int(input("Enter end port (1-1024): "))

        if not (1 <= start_p <= 1024 and 1 <= end_p <= 1024):
            print("Port must be between 1 and 1024.")
        elif start_p > end_p:
            print("End port must be greater than or equal to start port.")
        else:

    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()
    
            scanner = PortScanner(target_ip)
            print(f"Scanning {target_ip} from port {start_p} to {end_p}...")
            
            scanner.scan_range(start_p, end_p)
            open_ports = scanner.get_open_ports()

            print(f"--- Scan Results for {target_ip} ---")
            for p, stat, serv in open_ports:
                print(f"Port {p}: {stat} ({serv})")
            print("------")
            print(f"Total open ports found: {len(open_ports)}")

            save_results(target_ip, scanner.scan_results)

            history = input("Would you like to see past scan history? (yes/no): ").lower()
            if history == "yes":
                load_past_scans()
        
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root

# I propose adding a 'Scan Logging to Text' feature. By using the 'os' module to create a simple
# .txt file for every scan, the tool could provide a quick, portable report that the user can
# share or open in Notepad without needing to use a database viewer or write SQL queries.