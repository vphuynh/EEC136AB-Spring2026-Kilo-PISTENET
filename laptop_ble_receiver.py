# laptop_ble_receiver.py

from collections import deque
from mock_ble_device import MockBLEDevice
from parser import parse_data, print_parsed
from scoreboard import Scoreboard


class LaptopBLEReceiver:

    def __init__(self):
        # create the fake BLE device
        self.device = MockBLEDevice()

        # queue for incoming packets
        self.packet_queue = deque()

        # packet counter
        self.packet_count = 0

        # create the scoreboard object
        self.scoreboard = Scoreboard()

    # this function runs whenever a BLE notification comes in
    def handle_notification(self, sender, raw_bytes):
        # count new packet
        self.packet_count += 1

        print(f"Packet #{self.packet_count} arrived")
        print("Sender:", sender)
        print("Raw bytes:", raw_bytes)

        try:
            # convert bytes into normal text
            data = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            print("Decode error")
            print("----------------------")
            print()
            return

        print("Decoded:", data)

        # store packet in queue
        self.packet_queue.append(data)

        print("Queued packet. Queue size is now:", len(self.packet_queue))
        print()

    # this function processes one packet from the queue
    def process_next_packet(self):
        # if queue is empty, nothing to process
        if len(self.packet_queue) == 0:
            return

        # get oldest packet
        data = self.packet_queue.popleft()

        print("Now processing packet from queue:", data)

        # parse packet
        parsed = parse_data(data)

        # print parsed result
        print_parsed(parsed)

        # update scoreboard
        self.scoreboard.update_score(parsed)

        # print current scoreboard after each packet
        self.scoreboard.print_scoreboard()

        print("Queue size after processing:", len(self.packet_queue))
        print()

    # this function processes all packets in queue
    def process_all_packets(self):
        while len(self.packet_queue) > 0:
            self.process_next_packet()

    # this function starts the receiver
    def start(self):
        print("Receiver ready for incoming BLE data")
        print("Current mode: simulated BLE callback notifications with queue")
        print("Scoreboard mode: enabled\n")

        # receive notifications first
        self.device.start_notifications(self.handle_notification)

        # then process queued packets
        print("All notifications received")
        print("Now processing queued packets...\n")

        self.process_all_packets()