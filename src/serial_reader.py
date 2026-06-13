import serial
import json
import sys

class SerialTacticalReader:
    def __init__(self, port='/dev/ttyUSB1', baudrate=115200, timeout=1):
        """
        Initializes the reading interface.
        If testing locally with a virtual null-modem or loopback cable,
        this port should connect to the matching counter-port of your transmitter.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        """Establishes the physical hardware interface listening layer."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"[*] Tactical Reader listening on port: {self.port} at {self.baudrate} baud...")
        except serial.SerialException as e:
            print(f"[!] Reader failed to bind to hardware interface {self.port}: {e}")
            self.serial_connection = None

    def listen_loop(self):
        """Continuous block loop that intercepts, un-frames, and decodes incoming JSON streams."""
        if not self.serial_connection or not self.serial_connection.is_open:
            print("[!] Connection closed. Cannot begin operational read loop.")
            return

        print("[*] Waiting for incoming tactical packets. Press Ctrl+C to abort.")
        try:
            while True:
                # Read hardware line stream until a trailing newline character (\n) is detected
                raw_bytes = self.serial_connection.readline()
                
                if not raw_bytes:
                    continue # Timeout hit with no data, loop back to avoid freezing the thread
                
                try:
                    # Strip whitespace, decode from raw bytes to string
                    clean_string = raw_bytes.decode('utf-8').strip()
                    
                    # De-serialize the flat JSON packet back into a Python Dictionary
                    envelope = json.loads(clean_string)
                    
                    # Process and display the structured data packet
                    self._process_incoming_packet(envelope)
                    
                except json.JSONDecodeError:
                    print(f"[!] Corruption warning: Intercepted malformed data payload on line -> {raw_bytes}")
                except UnicodeDecodeError:
                    print("[!] Encoding error: Received data packet outside of UTF-8 encoding array spectrum.")
                    
        except KeyboardInterrupt:
            print("\n[*] Intercepted manual exit signal. Shutting down receiver engine.")

    def _process_incoming_packet(self, envelope):
        """Business logic execution layer for validated incoming JSON tracking payloads."""
        msg_type = envelope.get("msg_type", "UNKNOWN")
        timestamp = envelope.get("timestamp", 0)
        data = envelope.get("data", {})
        
        print("\n" + "="*50)
        print(f"[+] INTERCEPTED PACKET | TYPE: {msg_type} | EPOCH: {timestamp}")
        print("="*50)
        
        # Route processing behavior depending on payload telemetry flags
        if msg_type == "SITUATIONAL_TRACK" or msg_type == "ADS-B_TRACK":
            print(f" -> Track Target Hex Identification: {data.get('aircraft_id', data.get('hex'))}")
            print(f" -> Spatial Position Matrix: {data.get('coordinates', [data.get('lat'), data.get('lon')])}")
            print(f" -> Operational Altitude Ceiling: {data.get('altitude_hae_meters', data.get('alt_m'))} meters")
        else:
            print(f" -> Raw Data Context Captured: {json.dumps(data, indent=2)}")

    def close(self):
        """Gracefully drops the interface hardware allocation state."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("[*] Serial reader resource lock released cleanly.")

if __name__ == "__main__":
    # Standard hardware node execution hook
    # Adjust target ports to match your development platform maps (e.g. 'COM4' or '/dev/ttyUSB1')
    reader = SerialTacticalReader(port='/dev/ttyUSB1', baudrate=115200)
    reader.connect()
    reader.listen_loop()
    reader.close()
