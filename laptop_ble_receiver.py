# laptop_ble_receiver.py

from collections import deque
from mock_ble_device import MockBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard


class LaptopBLEReceiver:

    def __init__(self):
        self.device = MockBLEDevice()
        self.packet_queue = deque()
        self.packet_count = 0

        # use pool rules (first to 5)
        self.scoreboard = Scoreboard(bout_type="pool")

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

        # queue packet
        self.packet_queue.append(data)

        # immediately process (real-time behavior)
        self.process_next_packet()

    def process_next_packet(self):

        if len(self.packet_queue) == 0:
            return

        data = self.packet_queue.popleft()

        print("Now processing packet:", data)

        parsed = parse_data(data)

        print_parsed(parsed)

        self.scoreboard.update_score(parsed)

        self.scoreboard.print_scoreboard()

    def start(self):

        print("Receiver ready for incoming BLE data")
        print("Mode: LIVE processing with colors\n")

        self.device.start_notifications(self.handle_notification)

        print("\nAll packets processed")

        self.scoreboard.print_match_history()
        self.scoreboard.save_match_history()