# real_ble_device.py

# this file is for future real BLE integration
# the UUID values are placeholders until firmware gives us the real ones

DEVICE_NAME = "replace-with-psoc6-device-name"
SERVICE_UUID = "replace-with-psoc6-service-uuid"
CHARACTERISTIC_UUID = "replace-with-psoc6-characteristic-uuid"


class RealBLEDevice:

    def __init__(self):
        self.device_name = DEVICE_NAME
        self.service_uuid = SERVICE_UUID
        self.characteristic_uuid = CHARACTERISTIC_UUID

    def start_notifications(self, callback):

        print("Real BLE mode selected")
        print("Device name:", self.device_name)
        print("Service UUID:", self.service_uuid)
        print("Characteristic UUID:", self.characteristic_uuid)
        print()
        print("Real BLE connection is not enabled yet.")
        print("Waiting for hardware/firmware UUIDs before connecting.")
        print("For now, use mock BLE mode for testing.")