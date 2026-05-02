# laptop_ble_receiver.py

from collections import deque
from mock_ble_device import MockBLEDevice
from real_ble_device import RealBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard


class LaptopBLEReceiver:

    def __init__(self, mode="mock"):
        self.mode = mode
        self.packet_queue = deque()
        self.packet_count = 0

        # use pool rules first to 5
        # use de rules first to 15
        self.scoreboard = Scoreboard(bout_type="de")

        # choose between mock (testing) and real BLE (PSoC 6)
        if self.mode == "real":
            self.device = RealBLEDevice()
        else:
            self.mode = "mock"
            self.device = MockBLEDevice()

    def handle_notification(self, sender, raw_bytes):

        self.packet_count += 1

        print(f"\nPacket #{self.packet_count} arrived")
        print("Sender:", sender)
        print("Raw bytes:", raw_bytes)

        try:
            data = raw_bytes.decode("utf-8")
        except:
            print("Decode error")
            return

        print("Decoded:", data)

        # send decoded data into the normal software pipeline
        self.handle_packet_data(data)

    def handle_packet_data(self, data):

        # queue packet first
        self.packet_queue.append(data)

        # process immediately to keep real-time behavior
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

        self.scoreboard.print_scoreboard()

    def start(self):

        print("Receiver ready for incoming BLE data")
        print("Current mode:", self.mode)
        print(f"Scoreboard mode: {self.scoreboard.bout_type} bout, first to {self.scoreboard.winning_score}\n")

        # --- reset thread ---
        import threading

        def wait_for_reset():
            while True:
                cmd = input()
                if cmd.lower() == "r":
                    self.scoreboard.reset_match()
                    print("\n--- Match Reset ---\n")

        threading.Thread(target=wait_for_reset, daemon=True).start()
        # --- end reset thread ---

        self.device.start_notifications(self.handle_notification)
