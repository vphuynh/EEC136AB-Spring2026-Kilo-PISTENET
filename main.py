# main.py

from laptop_ble_receiver import LaptopBLEReceiver


def main():

    # change this to "mock" if you want to test without hardware
    mode = "real"

    receiver = LaptopBLEReceiver(mode=mode)
    receiver.start()


if __name__ == "__main__":
    main()