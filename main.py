# main.py

from laptop_ble_receiver import LaptopBLEReceiver


def main():
    # create the laptop BLE receiver
    receiver = LaptopBLEReceiver()

    # start the receiver
    receiver.start()


if __name__ == "__main__":
    main()