# Inside your src/main.py
from serial_bridge import SerialTacticalBridge

# 1. Spin up your physical link hardware controller
serial_link = SerialTacticalBridge(port='/dev/ttyUSB0', baudrate=115200)
serial_link.connect()

# 2. Inside your live data feed receiver loop:
def on_adsb_exchange_packet_received(raw_data):
    # Package into the structured format Rheinmetall requested
    formatted_track = {
        "aircraft_id": raw_data.get("hex"),
        "coordinates": [raw_data.get("lat"), raw_data.get("lon")],
        "altitude_hae_meters": raw_data.get("alt_geom", 0) * 0.3048
    }
    # Send it down the physical wire instantly
    serial_link.send_tactical_json(data_type="SITUATIONAL_TRACK", payload=formatted_track)

