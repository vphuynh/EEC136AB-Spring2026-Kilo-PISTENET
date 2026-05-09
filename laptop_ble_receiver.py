# laptop_ble_receiver.py

from collections import deque
from mock_ble_device import MockBLEDevice
from real_ble_device import RealBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard
from web_scoreboard import WebScoreboard


class LaptopBLEReceiver:

    def __init__(self, mode="mock"):
        self.mode = mode
        self.packet_queue = deque(maxlen=50)
        self.packet_count = 0

        self.device_status = {
            "Fencing_P1": "not connected",
            "Fencing_P2": "not connected"
        }

        self.scoreboard = Scoreboard(bout_type="de")
        self.scoreboard.device_status = self.device_status

        self.web_scoreboard = WebScoreboard(self.scoreboard)

        if self.mode == "real":
            self.device = RealBLEDevice()
            self.device.set_status_callback(self.update_device_status)
        else:
            self.mode = "mock"
            self.device = MockBLEDevice()

    def update_device_status(self, device_name, status):
        if device_name not in self.device_status:
            return
        self.device_status[device_name] = status
        self.scoreboard.device_status = self.device_status
        print(f"[STATUS] {device_name}: {status}")

    def handle_notification(self, sender, raw_bytes):

        self.packet_count += 1

        print("\n======================")
        print(f"Packet #{self.packet_count} arrived")
        print("Sender:", sender)
        print("Raw bytes:", raw_bytes)

        try:
            data = raw_bytes.decode("utf-8", errors="replace").strip()
        except:
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
        print("Web scoreboard running at: http://127.0.0.1:5000")

        print("Receiver ready for incoming BLE data")
        print("Current mode:", self.mode)
        print(f"Scoreboard mode: {self.scoreboard.bout_type} bout, first to {self.scoreboard.winning_score}")

        print("\nCommands:")
        print("r = reset match")
        print("q = quit program\n")

        import threading
        import os

        def command_loop():
            while True:
                cmd = input().strip().lower()

                if cmd == "r":
                    self.scoreboard.reset_match()
                    print("\n--- Match Reset ---\n")

                elif cmd == "q":
                    print("Manual quit selected")
                    os._exit(0)

                else:
                    print("Unknown command. Use r or q.")

        threading.Thread(target=command_loop, daemon=True).start()

        self.device.start_notifications(self.handle_notification)