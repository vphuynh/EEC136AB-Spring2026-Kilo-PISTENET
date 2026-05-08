import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAMES = ["Fencing_P1", "Fencing_P2"]


class RealBLEDevice:

    def __init__(self):
        self.device_names = DEVICE_NAMES
        self.status_callback = None

    def set_status_callback(self, callback):
        self.status_callback = callback

    def update_status(self, device_name, status):
        if self.status_callback:
            self.status_callback(device_name, status)

    def start_notifications(self, callback):
        try:
            asyncio.run(self.run_ble(callback))
        except KeyboardInterrupt:
            print("\nManual stop selected. BLE receiver closed.")

    async def connect_one_device(self, device_name, callback):

        while True:
            self.update_status(device_name, "scanning")
            print("Scanning for:", device_name)

            device = await BleakScanner.find_device_by_name(device_name, timeout=15)

            if device is None:
                self.update_status(device_name, "not found")
                print("Could not find", device_name)
                print("Trying again in 3 seconds...\n")
                await asyncio.sleep(3)
                continue

            print("Found:", device.name, device.address)

            try:
                async with BleakClient(device) as client:
                    self.update_status(device_name, "connected")
                    print("Connected to", device_name)

                    notify_char = None

                    for service in client.services:
                        for char in service.characteristics:
                            if "notify" in char.properties:
                                notify_char = char.uuid
                                break

                        if notify_char is not None:
                            break

                    if notify_char is None:
                        self.update_status(device_name, "no notify")
                        print("No notify characteristic found for", device_name)
                        print("Trying again in 3 seconds...\n")
                        await asyncio.sleep(3)
                        continue

                    def notification_handler(sender, raw_bytes):
                        print("\nNotification from:", device_name)
                        callback(sender, raw_bytes)

                    try:
                        await client.start_notify(notify_char, notification_handler)
                    except Exception as error:
                        self.update_status(device_name, "notify error")
                        print("Could not start notifications for", device_name)
                        print("Reason:", error)
                        print("Trying again in 3 seconds...\n")
                        await asyncio.sleep(3)
                        continue

                    print("Subscribed to", device_name)
                    print("Listening... press Ctrl+C to stop manually.\n")

                    while client.is_connected:
                        await asyncio.sleep(1)

                    self.update_status(device_name, "disconnected")
                    print(device_name, "disconnected")
                    print("Reconnecting in 3 seconds...\n")
                    await asyncio.sleep(3)

            except asyncio.CancelledError:
                self.update_status(device_name, "stopped")
                print("Stopped listening to", device_name)
                break

            except Exception as error:
                self.update_status(device_name, "error")
                print("BLE error with", device_name)
                print("Reason:", error)
                print("Trying again in 3 seconds...\n")
                await asyncio.sleep(3)

    async def run_ble(self, callback):
        print("Real BLE mode selected")
        print("Connecting to both devices...\n")

        await asyncio.gather(
            self.connect_one_device("Fencing_P1", callback),
            self.connect_one_device("Fencing_P2", callback)
        )