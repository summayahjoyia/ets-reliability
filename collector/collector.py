import requests
import csv
import os
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2

# The live vehicle position feed URL
VEHICLE_POSITIONS_URL = "https://gtfs.edmonton.ca/TMGTFSRealTimeWebService/Vehicle/VehiclePositions.pb"

# Where to save collected data
OUTPUT_FILE = "data/collected/vehicle_positions.csv"

def fetch_vehicle_positions():
    """Fetch current vehicle positions from ETS real-time feed."""
    response = requests.get(VEHICLE_POSITIONS_URL, timeout=30)
    response.raise_for_status()
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed

def save_positions(feed):
    """Parse feed and append observations to CSV."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        
        # Write header only if file is new
        if not file_exists:
            writer.writerow([
                "collected_at", "vehicle_id", "trip_id", 
                "route_id", "latitude", "longitude", 
                "timestamp", "current_stop_sequence"
            ])
        
        for entity in feed.entity:
            if entity.HasField("vehicle"):
                v = entity.vehicle
                writer.writerow([
                    timestamp,
                    v.vehicle.id,
                    v.trip.trip_id,
                    v.trip.route_id,
                    v.position.latitude,
                    v.position.longitude,
                    v.timestamp,
                    v.current_stop_sequence
                ])

def main():
    print(f"Fetching vehicle positions at {datetime.now(timezone.utc).isoformat()}")
    feed = fetch_vehicle_positions()
    save_positions(feed)
    print(f"Saved {len(feed.entity)} vehicle entities")

if __name__ == "__main__":
    main()