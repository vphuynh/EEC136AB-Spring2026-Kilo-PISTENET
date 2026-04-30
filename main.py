# main.py

from laptop_ble_receiver import LaptopBLEReceiver


def main():

    # use mock mode for Week 4 testing
    # change to "real" later when hardware UUIDs are ready
    receiver = LaptopBLEReceiver(mode="real")

    receiver.start()


if __name__ == "__main__":
    main()