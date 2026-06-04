# laptop_ble_receiver.py

from collections import deque
import serial
from serial.tools import list_ports
from real_ble_device import RealBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard
from web_scoreboard import WebScoreboard


class LaptopBLEReceiver:
    def find_repeater_port(self):

        ports = list_ports.comports()

        for port in ports:
            if "usbmodem" in port.device:
                return port.device

        return None

    def __init__(self):
        self.packet_queue = deque(maxlen=50)
        self.packet_count = 0

        self.device_status = {
            "Fencing_P1": "not connected",
            "Fencing_P2": "not connected"
        }

        self.scoreboard = Scoreboard(bout_type="de")
        self.scoreboard.device_status = self.device_status

        self.device = RealBLEDevice()
        self.device.set_status_callback(self.update_device_status)

        self.repeater = None
        self.connect_repeater()
        
        self.web_scoreboard = WebScoreboard(
                    self.scoreboard,
                    self.device,
                    self.send_score_to_repeater
                )

    def update_device_status(self, device_name, status):

        if device_name not in self.device_status:
            return

        old_status = self.device_status[device_name]

        self.device_status[device_name] = status
        self.scoreboard.device_status = self.device_status

        print(f"[STATUS] {device_name}: {status}")

        if old_status != status:
            self.scoreboard.add_system_event(
                f"{device_name} changed from {old_status} to {status}"
            )

    def handle_notification(self, sender, raw_bytes):

        self.packet_count += 1

        print("\n======================")
        print(f"Packet #{self.packet_count} arrived")
        print("Sender:", sender)
        print("Raw bytes:", raw_bytes)

        try:
            data = raw_bytes.decode("utf-8", errors="replace").strip()
        except UnicodeDecodeError:
            print("Decode error - packet ignored")
            return

        print(f"[BLE SENSOR OUTPUT] {data}")

        self.handle_packet_data(data)

    def handle_packet_data(self, data):

        self.packet_queue.append(data)
        self.process_next_packet()
    
    def connect_repeater(self):

        repeater_port = self.find_repeater_port()

        if repeater_port is None:
            print("Repeater not found")
            self.repeater = None
            return

        try:
            self.repeater = serial.Serial(
                repeater_port,
                115200,
                timeout=1
            )

            print("Repeater connected on", repeater_port)

        except Exception as e:
            print("Repeater connect error:", e)
            self.repeater = None


    def send_score_to_repeater(self):

        if self.repeater is None:
            self.connect_repeater()

        if self.repeater is None:
            return

        try:
            message = f"{self.scoreboard.player_1_score},{self.scoreboard.player_2_score}\n"
            self.repeater.write(message.encode("utf-8"))
            print("[REPEATER]", message.strip())

        except Exception as e:
            print("Repeater send error:", e)
            self.repeater = None
    
    def process_next_packet(self):

        if len(self.packet_queue) == 0:
            return

        data = self.packet_queue.popleft()

        print("Now processing packet:", data)

        parsed = parse_data(data)

        if parsed:
            print_parsed(parsed)
            self.scoreboard.update_score(parsed)
        else:
            print("Invalid packet - ignored")
            self.scoreboard.update_score(None)

        self.scoreboard.print_scoreboard()
        self.send_score_to_repeater()

    def start(self):

        self.web_scoreboard.start()

        print("\n==============================")
        print("   PISTENET BLE RECEIVER")
        print("==============================")
        print("Web scoreboard: http://127.0.0.1:5000")
        print(f"Scoreboard: {self.scoreboard.bout_type.upper()} bout, first to {self.scoreboard.winning_score}")
        print("Commands: r = reset match, q = quit, e/f/s = weapon mode changes")
        print("==============================\n")

        import threading
        import os

        def command_loop():
            while True:
                cmd = input().strip().lower()

                if cmd == "r":
                    self.packet_count = 0
                    self.scoreboard.reset_match()
                    self.send_score_to_repeater()
                    print("\n--- Match Reset ---\n")

                elif cmd == "q":
                    print("Manual quit selected")
                    os._exit(0)

                elif cmd == "o":
                    print("TEST OFFTARGET COMMAND RECEIVED")
                    self.handle_packet_data("P1,hit,0,123458")

                elif cmd == "e":
                    self.device.set_weapon_mode("epee")

                elif cmd == "f":
                    self.device.set_weapon_mode("foil")

                elif cmd == "s":
                    self.device.set_weapon_mode("saber")

                else:
                    print("Commands: r = reset match, q = quit, e/f/s = weapon mode")

        threading.Thread(target=command_loop, daemon=True).start()

        self.device.start_notifications(self.handle_notification)