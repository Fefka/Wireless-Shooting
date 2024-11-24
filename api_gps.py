import socket
import threading
import serial
import time

def handle_client(client_socket):
    """
    Obsługuje połączenie z jednym klientem.
    """
    try:
        while True:
            # Czytaj dane z portu szeregowego i wysyłaj do klienta
            if ser.is_open:
                data = ser.readline().decode('ascii', errors='ignore').strip()
                if data:
                    client_socket.sendall((data + '\n').encode('ascii'))
                    print(f"Wysłano: {data}")
            time.sleep(1)  # Odczekaj chwilę przed kolejnym odczytem
    except (socket.error, BrokenPipeError):
        print("Klient zakończył połączenie.")
    finally:
        client_socket.close()

def start_server(serial_port='/dev/ttyUSB0', baud_rate=9600, host='0.0.0.0', port=8080):
    """
    Serwer TCP obsługujący wielu klientów, przesyłający dane z portu szeregowego.
    """
    global ser
    ser = serial.Serial(serial_port, baud_rate, timeout=1)  # Inicjalizacja portu szeregowego
    print(f"Port szeregowy otwarty: {serial_port} na prędkości {baud_rate} bps.")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Serwer nasłuchuje na {host}:{port}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Połączono z klientem: {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
    finally:
        if ser.is_open:
            ser.close()
        server_socket.close()

if __name__ == "__main__":
    start_server()
