# PisteNet

PisteNet is a wireless fencing scoring system that uses two BLE-enabled player devices, a laptop receiver, and a scoreboard interface to track and display fencing bout results in real time.

## Features
- BLE hit detection from two player devices
- Real-time web scoreboard
- Multiple weapon modes (Epee, Foil, Saber)
- Pool and Direct Elimination bout presets
- Serial repeater support for external displays
- Match history and event logging

## How to run

1. Install Python (3.10+)
2. Install dependencies:
    pip install bleak colorama flask pyserial
3. Run:
    python3 main.py

Make sure:
- Both PSoC devices are powered
- Device names: Fencing_P1 and Fencing_P2

## Terminal commands

r = reset match

q = quit program

e/f/s = weapon mode change

for web scoreboard: 

open http://127.0.0.1:5000

The browser repeater page is available at:

http://127.0.0.1:5000/repeater

The primary repeater used during demonstrations is the Pico Unicorn serial repeater.

## Keyboard Shortcuts

Space = Start / Pause Timer

R = Reset Match

1 = Add Point to P1

2 = Add Point to P2

3 = Subtract Point to P1

4 = Subtract Point to P2

E = Epee Mode

F = Foil Mode

S = Saber Mode

V = Showcase Mode

G = Fullscreen
