import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAMES = ["Fencing_P1", "Fencing_P2"]
WEAPON_UUID = "9BED9980-6371-4B74-A021-9AE863131F63"


class RealBLEDevice:

    def __init__(self):
        self.device_names = DEVICE_NAMES
        self.status_callback = None
        self.weapon_mode = "epee"
        self.last_sent_weapon = {}

    def set_status_callback(self, callback):
        self.status_callback = callback

    def set_weapon_mode(self, weapon_mode):
        self.weapon_mode = weapon_mode
        print("[BLE COMMAND] weapon mode set to:", weapon_mode)

    def update_status(self, device_name, status):
        if self.status_callback:
            self.status_callback(device_name, status)

    def start_notifications(self, callback):
        try:
            asyncio.run(self.run_ble(callback))
        except KeyboardInterrupt:
            print("\nManual stop selected. BLE receiver closed.")
        except Exception as error:
            print("BLE receiver stopped because of an error:")
            print(error)

    async def connect_one_device(self, device_name, callback):

        while True:
            try:
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

                async with BleakClient(device) as client:
                    self.update_status(device_name, "connected")
                    print("Connected to", device_name)
                    print("Weapon UUID:", WEAPON_UUID)

                    notify_char = None
                    write_char = WEAPON_UUID
                    write_with_response = True

                    for service in client.services:
                        for char in service.characteristics:

                            if notify_char is None and "notify" in char.properties:
                                notify_char = char.uuid

                            if write_char is None:
                                if "write" in char.properties or "write-without-response" in char.properties:
                                    write_char = char.uuid

                                    if "write-without-response" in char.properties and "write" not in char.properties:
                                        write_with_response = False

                        if notify_char is not None and write_char is not None:
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

                        if write_char is not None:
                            last_sent = self.last_sent_weapon.get(device_name)

                            if last_sent != self.weapon_mode:
                                command = "weapon," + self.weapon_mode

                                try:
                                    await client.write_gatt_char(
                                        write_char,
                                        command.encode("utf-8"),
                                        response=write_with_response
                                    )

                                    self.last_sent_weapon[device_name] = self.weapon_mode
                                    print("[BLE WRITE]", device_name, "sent:", command)

                                except Exception as error:
                                    print("[BLE WRITE ERROR]", device_name, error)

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

        results = await asyncio.gather(
            self.connect_one_device("Fencing_P1", callback),
            self.connect_one_device("Fencing_P2", callback),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, Exception):
                print("BLE task ended with error:", result)