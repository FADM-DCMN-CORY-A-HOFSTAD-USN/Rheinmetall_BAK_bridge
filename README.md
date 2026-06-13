# Rheinmetall BAK Tactical D-LBO Aviation Software Bridge

This engineering repository houses the tactical data bridging engine built to interface custom python-based aviation platforms with Rheinmetall’s Digitalization of Land-Based Operations (**D-LBO**) ecosystem framework. 

The software acts as a processing gateway. It transforms unencrypted, open-source civilian aviation tracks and geospatial telemetry datasets into highly structured payloads for direct physical ingestion across vehicular hardware edge nodes.

---

## Architecture Overview

The system bypasses heavy network middleware overhead by executing a point-to-point **JSON-over-Serial transmission layer**. This strategy allows low-latency injection directly into local data processing hardware hubs or tactical software-defined radio interfaces (e.g., Rohde & Schwarz SOVERON systems).

```text
 [Civilian Aviation Data Ingestion Layer]
   │  (ADS-B Exchange Streams & Logistical GeoJSON Elements)
   ▼
 [src/cot_bridge.py] ──> Transforms inputs to MIL-STD Cursor-on-Target formats
   │
   ▼
 [src/serial_bridge.py] ──> Encapsulates to JSON + Adds framing lines (\n)
   │
   ▼  (Physical Serial Interface Link: RS-232 / RS-422 / USB UART)
   │
 [Rheinmetall Edge Nodes / D-LBO Tactical Gateway]
```

---

## Directory Structure Blueprint

Ensure your active runtime environment matches the structural design below:

```text
Rheinmetall_BAK_bridge/
├── requirements.txt            # Operational system requirements configuration
├── README.md                   # System design blueprint documentation
└── src/                        # Core engineering production module group
    ├── __init__.py             # Module initialization namespace map
    ├── cot_bridge.py           # MIL-STD tactical markup transformation engine
    ├── serial_bridge.py        # Serial data serialization transmitter controller
    └── serial_reader.py        # Simulated Rheinmetall D-LBO hardware parser receiver
```

---

## Environmental Setup & Installation

1. Clone this tactical code assembly layout to your local operations machine.
2. Initialize an isolated virtual environment and load the declared infrastructure libraries:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Local Verification Testing Loop

You can simulate a physical serial link loopback directly on your local system without military hardware attachments.

### Step 1: Instantiate the Virtual Serial Bridge
Open an isolated command terminal pipeline and map two virtual communication channels together using `socat`:

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```
*This command outputs two linked target paths (e.g., `/dev/pts/2` and `/dev/pts/3`).*

### Step 2: Spin Up the Simulated Receiver Node
Open a second terminal loop, configure the script port to point to the **second** virtual path, and launch the reader loop to monitor input processing:

```bash
# Set port parameter inside src/serial_reader.py to match your second virtual path
python3 src/serial_reader.py
```

### Step 3: Trigger the Transmitter Payload Bridge
Open a third terminal window, bind the transmitter parameters to the **first** virtual path, and execute the runtime thread to dispatch live tracking vectors across the bridge:

```bash
# Set port parameter inside src/serial_bridge.py to match your first virtual path
python3 src/serial_bridge.py
```

---

## Interface Integration Control Vector Specification

All data traversing the serial cable boundary uses a standard telemetry framing structure:

```json
{
  "version": "1.0",
  "msg_type": "SITUATIONAL_TRACK",
  "timestamp": 1718222400,
  "data": {
    "aircraft_id": "3C66A2",
    "coordinates": [52.5200, 13.4050],
    "altitude_hae_meters": 9753.6
  }
}
```
*Note: Every packet transmitted down the hardware line is appended with a trailing `\n` line-break byte string. This character serves as the mandatory message-frame end indicator for real-time memory buffer parsing filters.*
