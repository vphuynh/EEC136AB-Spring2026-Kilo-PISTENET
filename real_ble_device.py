import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAMES = ["Fencing_P1", "Fencing_P2"]


class RealBLEDevice:

    def __init__(self):
        self.device_names = DEVICE_NAMES

    def start_notifications(self, callback):
        asyncio.run(self.run_ble(callback))

    async def connect_one_device(self, device_name, callback):
        print("Scanning for:", device_name)

        device = await BleakScanner.find_device_by_name(device_name, timeout=15)

        if device is None:
            print("Could not find", device_name)
            return

        print("Found:", device.name, device.address)

        async with BleakClient(device) as client:
            print("Connected to", device_name)

            notify_char = None

            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        notify_char = char.uuid

            if notify_char is None:
                print("No notify characteristic found for", device_name)
                return

            def notification_handler(sender, raw_bytes):
                print("\nNotification from:", device_name)
                callback(sender, raw_bytes)
            #
            try:
                await client.start_notify(notify_char, notification_handler)
            except Exception as error:
                print("Could not start notifications for", device_name)
                print("Reason:", error)
                return
            
            print("Subscribed to", device_name)

            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                print("Stopped listening to", device_name)

    async def run_ble(self, callback):
        print("Real BLE mode selected")
        print("Connecting to both devices...\n")


        results = await asyncio.gather(
            self.connect_one_device("Fencing_P1", callback),
            self.connect_one_device("Fencing_P2", callback),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, Exception):
                print("BLE task ended with error:", result)