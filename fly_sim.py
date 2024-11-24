mport socket
import threading
import time
from pyproj import Proj, Transformer
from scipy.optimize import minimize
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import warnings

# Ignorowanie ostrzeżeń GLib-GIO
warnings.filterwarnings("ignore", category=UserWarning, module="gi.repository")

# Ustawienie projekcji WGS84 na UTM
wgs84 = Proj(proj="latlong", datum="WGS84")
utm_proj = Proj(proj="utm", zone=34, datum="WGS84")  # UTM Zone 34 (dla Polski)
transformer = Transformer.from_proj(wgs84, utm_proj)

# Słowniki przechowujące pozycje dronów
drone_positions = {"ATOS": (495000, 3398000), "PORTOS": (495200, 3398200), "ARTEMIS": (495400, 3398100), "ENEMY": (495300, 3398050)}

# Funkcja do symulacji odbioru danych z dronów
def handle_drone_simulation(drone_name):
    """Symuluje odbieranie danych o pozycjach dronów."""
    global drone_positions
    while True:
        x, y = drone_positions[drone_name]
        dx, dy = np.random.uniform(-10, 10, 2)  # Losowe przesunięcie
        drone_positions[drone_name] = (x + dx, y + dy)
        time.sleep(1)

# Funkcja do rysowania mapy i dynamicznej aktualizacji pozycji dronów
def plot_map_with_drones_dynamic(tiff_path):
    """Dynamiczna aktualizacja mapy z pozycjami dronów i przeciwnika."""
    with rasterio.open(tiff_path) as src:
        map_data = src.read(1)
        bounds = src.bounds

    # Granice mapy (UTM)
    map_min_x, map_min_y = bounds.left, bounds.bottom
    map_max_x, map_max_y = bounds.right, bounds.top

    # Poszerzenie zakresu skali mapy
    scale_buffer = 100  # 100 metrów zapasu na każdej osi
    map_min_x -= scale_buffer
    map_max_x += scale_buffer
    map_min_y -= scale_buffer
    map_max_y += scale_buffer

    # Wykres
    fig, ax = plt.subplots(figsize=(10, 10))
    img = ax.imshow(map_data, extent=[map_min_x, map_max_x, map_min_y, map_max_y], cmap="gray", origin="upper")

    # Punkty dronów i przeciwnika z różnymi kolorami
    atos_point, = ax.plot([], [], 'o', label="ATOS", color="steelblue", markersize=10)
    portos_point, = ax.plot([], [], 'o', label="PORTOS", color="greenyellow", markersize=10)
    artemis_point, = ax.plot([], [], 'o', label="ARTEMIS", color="deeppink", markersize=10)
    enemy_point, = ax.plot([], [], '*', label="ENEMY", color="red", markersize=12)

    # Aktualizacja danych
    def update(frame):
        atos_x, atos_y = drone_positions["ATOS"]
        portos_x, portos_y = drone_positions["PORTOS"]
        artemis_x, artemis_y = drone_positions["ARTEMIS"]
        enemy_x, enemy_y = drone_positions["ENEMY"]

        atos_point.set_data([atos_x], [atos_y])
        portos_point.set_data([portos_x], [portos_y])
        artemis_point.set_data([artemis_x], [artemis_y])
        enemy_point.set_data([enemy_x], [enemy_y])

        return atos_point, portos_point, artemis_point, enemy_point

    ani = FuncAnimation(fig, update, interval=1000)
    ax.legend(loc="upper right")
    ax.set_title("Pozycje dronów i przeciwnika w czasie rzeczywistym")
    ax.set_xlabel("UTM X (m)")
    ax.set_ylabel("UTM Y (m)")
    plt.colorbar(img, ax=ax, label="Wartości pikseli")
    plt.show()

# Główna logika programu
def main():
    # Ścieżka do mapy GeoTIFF
    tiff_path = "openEO_2024-11-23Z.tif"

    # Uruchomienie wątków symulujących ruch dronów
    threads = []
    for name in ["ATOS", "PORTOS", "ARTEMIS", "ENEMY"]:
        thread = threading.Thread(target=handle_drone_simulation, args=(name,))
        threads.append(thread)
        thread.start()

    # Wykres mapy z dynamiczną aktualizacją pozycji
    plot_map_with_drones_dynamic(tiff_path)

    # Zatrzymanie wątków po zakończeniu
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()