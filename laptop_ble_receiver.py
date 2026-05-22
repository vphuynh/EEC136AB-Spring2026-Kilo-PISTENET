# laptop_ble_receiver.py

from collections import deque
from real_ble_device import RealBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard
from web_scoreboard import WebScoreboard


class LaptopBLEReceiver:

    def __init__(self):
        self.packet_queue = deque(maxlen=50)
        self.packet_count = 0

        self.device_status = {
            "Fencing_P1": "not connected",
            "Fencing_P2": "not connected"
        }

        self.scoreboard = Scoreboard(bout_type="de")
        self.scoreboard.device_status = self.device_status

        self.web_scoreboard = WebScoreboard(self.scoreboard)

        self.device = RealBLEDevice()
        self.device.set_status_callback(self.update_device_status)

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

    def start(self):

        self.web_scoreboard.start()

        print("\n==============================")
        print("   PISTENET BLE RECEIVER")
        print("==============================")
        print("Web scoreboard: http://127.0.0.1:5000")
        print(f"Scoreboard: {self.scoreboard.bout_type.upper()} bout, first to {self.scoreboard.winning_score}")
        print("Commands: r = reset match, q = quit")
        print("==============================\n")

        import threading
        import os

        def command_loop():
            while True:
                cmd = input().strip().lower()

                if cmd == "r":
                    self.packet_count = 0
                    self.scoreboard.reset_match()
                    print("\n--- Match Reset ---\n")

                elif cmd == "q":
                    print("Manual quit selected")
                    os._exit(0)

                else:
                    print("Unknown command. Use r or q.")

        threading.Thread(target=command_loop, daemon=True).start()

        self.device.start_notifications(self.handle_notification)