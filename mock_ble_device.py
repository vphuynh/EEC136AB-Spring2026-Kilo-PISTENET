# mock_ble_device.py

import time


# this class pretends to be the future BLE hardware
class MockBLEDevice:

    def __init__(self):

        # fake packet data for testing
        # includes duplicate hits on purpose
        self.packets = [
            "P1,hit,100001",
            "P2,hit,100002",
            "P1,hit,100003",
            "P1,hit,100004",
            "P2,hit,100005",
            "P1,hit,100006",
            "P1,hit,100007",
            "P2,hit,100008"
        ]

    # this function simulates BLE notifications
    def start_notifications(self, callback):

        # go through packets one at a time
        for packet in self.packets:
            time.sleep(1)

            # real BLE sends bytes, so convert text into bytes
            raw_bytes = packet.encode("utf-8")

            # fake sender id
            sender = "mock_characteristic"

            # call the callback
            callback(sender, raw_bytes)