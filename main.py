# main.py

from laptop_ble_receiver import LaptopBLEReceiver


def main():

    receiver = LaptopBLEReceiver()
    receiver.start()


if __name__ == "__main__":
    main()