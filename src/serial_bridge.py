import serial
import json
import time

class SerialTacticalBridge:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        """
        Initializes the serial interface.
        Common military/industrial baudrates: 115200 or 9600.
        Default port '/dev/ttyUSB0' is common for Linux edge computers. Use 'COM3' for Windows.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        """Establishes the physical hardware connection layer."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"[*] Successfully connected to serial port: {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"[!] Hardware connection failure on {self.port}: {e}")
            self.serial_connection = None

    def send_tactical_json(self, data_type, payload):
        """
        Structures, stringifies, and transmits data over the serial connection.
        Appends a trailing newline delimiter so the receiving hardware knows the packet is complete.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            print("[!] Cannot transmit. Serial port is closed.")
            return False

        # Wrap data in a clean envelope detailing the message type and timestamp
        envelope = {
            "version": "1.0",
            "msg_type": data_type, # e.g., "ADS-B_TRACK" or "STATIC_SHAPE"
            "timestamp": int(time.time()),
            "data": payload
        }

        try:
            # Convert dict to flat JSON string, add newline string delimiter
            json_string = json.dumps(envelope) + "\n"
            # Encode string into raw bytes and push over physical tx line
            byte_payload = json_string.encode('utf-8')
            
            self.serial_connection.write(byte_payload)
            self.serial_connection.flush() # Force hardware buffer clear
            return True
        except Exception as e:
            print(f"[!] Error writing payload to serial line: {e}")
            return False

    def close(self):
        """Gracefully releases the serial port hardware lock."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("[*] Serial port interface closed cleanly.")

# --- VERIFICATION LOOP ---
if __name__ == "__main__":
    # Local loopback testing tip: If you don't have a hardware device plugged in,
    # you can test via virtual ports using 'socat' on Linux.
    
    bridge = SerialTacticalBridge(port='/dev/ttyUSB0', baudrate=115200)
    bridge.connect()

    mock_track = {"hex": "3c66a2", "lat": 52.5200, "lon": 13.4050, "alt_m": 9753, "gs_ms": 216.2}
    
    # Attempt to transmit a mock track packet over the line
    bridge.send_tactical_json(data_type="ADS-B_TRACK", payload=mock_track)
    
    bridge.close()

