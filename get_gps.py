import socket
import threading
import time
from pyproj import Proj, Transformer
from scipy.optimize import minimize
import numpy as np
import openeo
import rasterio
import matplotlib.pyplot as plt

# Ustawienie projekcji WGS84 na UTM
wgs84 = Proj(proj="latlong", datum="WGS84")
utm_proj = Proj(proj="utm", zone=34, datum="WGS84")  # UTM Zone 34 (dla Polski)
transformer = Transformer.from_proj(wgs84, utm_proj)

# Słowniki przechowujące pozycje dronów i odległości
drone_positions = {}
distances = {}
DELAY_SECONDS = 5  # Czas między obliczeniami pozycji przeciwnika

def parse_gpgga(sentence):
    """
    Parsuje zdanie NMEA typu GPGGA i wyodrębnia współrzędne GPS.
    """
    try:
        parts = sentence.split(',')
        if parts[0] != "$GPGGA":
            return None  # Tylko GPGGA jest obsługiwane

        lat_raw = parts[2]
        lat_dir = parts[3]
        lon_raw = parts[4]
        lon_dir = parts[5]
        alt = float(parts[9]) if parts[9] else 0.0

        if not lat_raw or not lon_raw:
            return None

        lat_deg = float(lat_raw[:2])
        lat_min = float(lat_raw[2:])
        latitude = lat_deg + lat_min / 60
        if lat_dir == "S":
            latitude = -latitude

        lon_deg = float(lon_raw[:3])
        lon_min = float(lon_raw[3:])
        longitude = lon_deg + lon_min / 60
        if lon_dir == "W":
            longitude = -longitude

        return latitude, longitude, alt
    except (IndexError, ValueError):
        return None

def convert_to_utm(lat, lon, alt):
    """
    Konwertuje współrzędne GPS (WGS84) na UTM.
    """
    utm_x, utm_y = transformer.transform(lat, lon)
    return utm_x, utm_y, alt

def convert_to_wgs84(utm_x, utm_y):
    """
    Konwertuje współrzędne UTM na WGS84.
    """
    lon, lat = transformer.transform(utm_x, utm_y, direction="INVERSE")
    return lat, lon

def calculate_aoi(drone_coords, enemy_coords, buffer_km=1.0):
    """
    Oblicza obszar zainteresowania (AOI) z ograniczeniem rozmiaru.
    """
    all_coords = drone_coords + [enemy_coords]
    center_lat = np.mean([coord[0] for coord in all_coords])
    center_lon = np.mean([coord[1] for coord in all_coords])

    # Przelicz bufor na stopnie (~1° to ok. 111 km)
    buffer_deg = buffer_km / 111.0

    return {
        "west": center_lon - buffer_deg,
        "east": center_lon + buffer_deg,
        "south": center_lat - buffer_deg,
        "north": center_lat + buffer_deg
    }

def handle_drone(ip, port, drone_name):
    """
    Obsługuje połączenie z jednym dronem, odbierając dane, konwertując na UTM i zapisując do słowników.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((ip, port))
            print(f"Connected with drone {drone_name} ({ip}:{port}).")

            while True:
                data = sock.recv(1024)
                if data:
                    message = data.decode('ascii').strip()
                    gps_data = parse_gpgga(message)
                    if gps_data:
                        lat, lon, alt = gps_data
                        utm_x, utm_y, utm_alt = convert_to_utm(lat, lon, alt)
                        drone_positions[drone_name] = (lat, lon)  # Przechowuj w WGS84
                        distances[drone_name] = np.random.uniform(10, 30)  # Przykładowe dane
                        print(f"{drone_name} Position (UTM): x = {utm_x:.2f}, y = {utm_y:.2f}, alt = {utm_alt:.1f}m")
                    else:
                        print(f"Unable to parse GPS data: {message}")
    except socket.timeout:
        print(f"Error: No response from drone {drone_name} ({ip}:{port}). Check the connection.")
    except Exception as e:
        print(f"Error connecting to {drone_name} ({ip}:{port}): {e}")

def triangulate(drone_coords, ranges):
    """
    Oblicza współrzędne przeciwnika na podstawie triangulacji.
    """
    def objective_function(p):
        x, y = p
        return sum((np.sqrt((x - cx)**2 + (y - cy)**2) - r)**2 for (cx, cy), r in zip(drone_coords, ranges))

    x0 = np.mean([coord[0] for coord in drone_coords])
    y0 = np.mean([coord[1] for coord in drone_coords])

    result = minimize(objective_function, (x0, y0), method='L-BFGS-B')
    if result.success:
        return result.x
    else:
        raise ValueError("Triangulation failed.")

def download_copernicus_map(drone_coords, enemy_coords):
    """
    Pobiera mapę EVI z Copernicus Data Space Ecosystem dla obszaru dronów i przeciwnika,
    zapisuje jako GeoTIFF i konwertuje na PNG.
    """
    print("Downloading map...")

    wgs84_drone_coords = [convert_to_wgs84(*convert_to_utm(lat, lon, 0)[:2]) for lat, lon in drone_coords]
    wgs84_enemy_coords = convert_to_wgs84(*convert_to_utm(*enemy_coords, 0)[:2])
    aoi = calculate_aoi(wgs84_drone_coords, wgs84_enemy_coords, buffer_km=1.0)

    print(f"Area of Interest (AOI): {aoi}")

    try:
        connection = openeo.connect("https://openeo.dataspace.copernicus.eu/")
        connection.authenticate_oidc(store_refresh_token=True)
        print("Connected to Copernicus Data Space.")

        datacube = connection.load_collection(
            "SENTINEL2_L2A",
            spatial_extent=aoi,
            temporal_extent=["2024-11-23", "2024-11-23"],
            bands=["B08", "B04", "B02"]  # NIR, RED, BLUE
        )
        evi_cube = (
            datacube.band("B08").subtract(datacube.band("B04"))
            .divide(
                datacube.band("B08")
                .add(datacube.band("B04").multiply(6))
                .subtract(datacube.band("B02").multiply(7.5))
                .add(1)
            )
            .multiply(2.5)
        )

        # Zapis GeoTIFF z pasmami
        geotiff_path = "/root/map_evi_with_bands.tif"
        result = evi_cube.save_result(format="GTiff")
        job = result.execute_batch()
        job.get_results().download_files(target="/root/")

        print(f"EVI map saved as GeoTIFF with bands: {geotiff_path}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    atos_thread = threading.Thread(target=handle_drone, args=("192.168.2.104", 8080, "ATOS"))
    artemis_thread = threading.Thread(target=handle_drone, args=("192.168.2.107", 8080, "ARTEMIS"))
    portos_thread = threading.Thread(target=handle_drone, args=("192.168.2.191", 8080, "PORTOS"))

    atos_thread.start()
    artemis_thread.start()
    portos_thread.start()

    try:
        while True:
            if len(drone_positions) == 3:
                drone_coords = [drone_positions[name] for name in ["ATOS", "ARTEMIS", "PORTOS"]]
                ranges = [distances[name] for name in ["ATOS", "ARTEMIS", "PORTOS"]]
                enemy_coords = triangulate([convert_to_utm(*pos, 0)[:2] for pos in drone_coords], ranges)
                download_copernicus_map(drone_coords, convert_to_wgs84(*enemy_coords))
                break
            time.sleep(DELAY_SECONDS)
    except KeyboardInterrupt:
        print("Program terminated.")

if __name__ == "__main__":
    main()
