# Raspberry Pi Pico (RP2040) MIDI Drum Machine - Rotary Test
# 2022 DCooper Dalrymple - me@dcdalrymple.com
# GPL v2 License
# Version 1.0

import time
import board
from digitalio import DigitalInOut, Direction, Pull
from rotaryio import IncrementalEncoder
from adafruit_debouncer import Debouncer

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Wait for USB to stabilize
time.sleep(0.5)

# Serial Header
print("RPi Pico Drum - Rotary Test")
print("Version 1.0")
print("Cooper Dalrymple, 2022")
print("https://dcdalrymple.com/rpi-pico-drum/")

print("\n:: Initializing Encoders ::")
menu_encoder = IncrementalEncoder(board.GP12, board.GP13)
menu_position = None
menu_button_pin = DigitalInOut(board.GP7)
menu_button_pin.direction = Direction.INPUT
menu_button_pin.pull = Pull.UP
menu_button = Debouncer(menu_button_pin)

mod_encoder = IncrementalEncoder(board.GP26, board.GP27)
mod_position = None
mod_button_pin = DigitalInOut(board.GP28)
mod_button_pin.direction = Direction.INPUT
mod_button_pin.pull = Pull.UP
mod_button = Debouncer(mod_button_pin)

print("\n:: Watching Encoders ::")

while True:
    position = menu_encoder.position
    if menu_position is None or position != menu_position:
        print("Menu:", position)
    menu_position = position

    position = mod_encoder.position
    if mod_position is None or position != mod_position:
        print("Mod:", position)
    mod_position = position

    menu_button.update()
    if menu_button.fell:
        print("Menu: Press")
    elif menu_button.rose:
        print("Menu: Release")

    mod_button.update()
    if mod_button.fell:
        print("Mod: Press")
    elif mod_button.rose:
        print("Mod: Release")

led.value = False
