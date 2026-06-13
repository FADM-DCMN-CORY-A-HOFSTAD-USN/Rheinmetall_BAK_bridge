import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import uuid

class TacticalCotBridge:
    def __init__(self, sender_uid="AviationBridge_01"):
        self.sender_uid = sender_uid

    def _generate_base_cot(self, cot_type, uid, stale_seconds=30):
        """Generates the standard structural envelope for a MIL-STD Cursor-on-Target event."""
        now = datetime.now(timezone.utc)
        stale = datetime.fromtimestamp(now.timestamp() + stale_seconds, timezone.utc)
        
        time_str = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        stale_str = stale.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        event = ET.Element("event", {
            "version": "2.0",
            "uid": uid,
            "type": cot_type,
            "time": time_str,
            "start": time_str,
            "stale": stale_str,
            "how": "h-e"  # Electronic input tracking
        })
        return event

    def parse_adsb_to_cot(self, adsb_track):
        """
        Converts live situational ADS-B data streams into military Air Tracks.
        Maps MIL-STD-2525 friendly/hostile/neutral indicators via standard type definitions.
        """
        # "a-f-A-M" translates to: Atom (a) - Friendly (f) - Air (A) - Military (M/Civilian Track)
        cot_type = "a-f-A" 
        uid = f"ICAO-{adsb_track.get('hex', 'UNKNOWN').upper()}"
        
        root = self._generate_base_cot(cot_type, uid, stale_seconds=15)
        
        # Point spatial coordinates 
        ET.SubElement(root, "point", {
            "lat": str(adsb_track.get("lat", 0.0)),
            "lon": str(adsb_track.get("lon", 0.0)),
            "hae": str(adsb_track.get("alt_geom", 0.0) * 0.3048),  # Feet to Meters HAE conversion
            "ce": "10.0",   # Circular error estimate
            "le": "5.0"     # Linear error estimate
        })
        
        # Tactical Metadata extensions
        detail = ET.SubElement(root, "detail")
        ET.SubElement(detail, "track", {
            "speed": str(adsb_track.get("gs", 0.0) * 0.514444), # Knots to Meters/Sec conversion
            "course": str(adsb_track.get("track", 0.0))
        })
        ET.SubElement(detail, "contact", {
            "callsign": adsb_track.get("flight", "UNK_CALL").strip()
        })
        
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

    def parse_geojson_shape_to_cot(self, geojson_feature, shape_name="Restricted_Zone"):
        """
        Converts static logistical polygon geometries into a tactical airspace boundary shape.
        Utilizes the drawing schema extension natively understood by military routing tools.
        """
        # "a-f-G-I" translates to: Atom (a) - Friendly (f) - Ground (G) - Infrastructure/Area (I)
        cot_type = "a-f-G-I"
        uid = f"SHAPE-{uuid.uuid4().hex[:8].upper()}"
        
        root = self._generate_base_cot(cot_type, uid, stale_seconds=86400) # 24 hour long lifecycle
        
        # Center reference point calculated from first polygon boundary index
        coordinates = geojson_feature["geometry"]["coordinates"][0]
        start_lat, start_lon = coordinates[0][1], coordinates[0][0]
        
        ET.SubElement(root, "point", {
            "lat": str(start_lat), "lon": str(start_lon), "hae": "0.0", "ce": "1.0", "le": "1.0"
        })
        
        detail = ET.SubElement(root, "detail")
        ET.SubElement(detail, "contact", {"callsign": shape_name})
        
        # Inject standard structural drawing markup for polygon perimeter lines
        link_dir = ET.SubElement(detail, "link_relation")
        for idx, coord in enumerate(coordinates):
            ET.SubElement(link_dir, "link", {
                "uid": uid,
                "type": "a-f-G-I",
                "relation": "g-p-p", # Polygon point reference tag
                "lat": str(coord[1]),
                "lon": str(coord[0]),
                "hae": "0.0",
                "order": str(idx)
            })
            
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

# --- EXECUTION / VERIFICATION LOOP ---
if __name__ == "__main__":
    bridge = TacticalCotBridge()

    # Mock Data Input Examples matching your real operational infrastructure
    mock_adsb_payload = {
        "hex": "3c66a2", 
        "flight": "DLH123 ", 
        "lat": 52.5200, 
        "lon": 13.4050, 
        "alt_geom": 32000, 
        "gs": 420.5, 
        "track": 270.0
    }
    
    mock_geojson_polygon = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [13.400, 52.510], [13.420, 52.510], 
                [13.420, 52.530], [13.400, 52.530], [13.400, 52.510]
            ]]
        }
    }

    print("=== LIVE ADS-B TRACK XML TO TACTICAL EDGE ===")
    print(bridge.parse_adsb_to_cot(mock_adsb_payload))
    
    print("\n=== LOGISTICAL GEOSPATIAL POLYGON TO TACTICAL EDGE ===")
    print(bridge.parse_geojson_shape_to_cot(mock_geojson_polygon, "ED-R_RESTRICTED_AIRSPACE"))
