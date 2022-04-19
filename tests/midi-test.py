# Raspberry Pi Pico (RP2040) MIDI Drum Machine - MIDI Test
# 2022 DCooper Dalrymple - me@dcdalrymple.com
# GPL v2 License
# Version 1.0

import time
import board

from digitalio import DigitalInOut, Direction, Pull
from busio import UART
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.program_change import ProgramChange

# Program Constants

MIDI_CHANNEL      = 10
MIDI_THRU         = False

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Wait for USB to stabilize
time.sleep(0.5)

# Serial Header
print("RPi Pico Drum - MIDI Test")
print("Version 1.0")
print("Cooper Dalrymple, 2022")
print("https://dcdalrymple.com/rpi-pico-drum/")

print("\n:: Initializing Midi ::")
uart = UART(
    tx=board.GP4,
    rx=board.GP5,
    baudrate=31250,
    timeout=0.001
)
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=MIDI_CHANNEL-1,
    out_channel=MIDI_CHANNEL-1,
    debug=False
)
print("Channel:", midi.in_channel+1)

print("\n:: Watching Midi ::")

while True:
    msg_in = midi.receive()
    if msg_in != None:
        if MIDI_THRU:
            midi.send(msg_in)
        if isinstance(msg_in, NoteOn):
            print("Note On:", msg_in.note, msg_in.velocity / 127.0)
        elif isinstance(msg_in, NoteOff):
            print("Note Off:", msg_in.note)

print("\n:: Complete ::")
led.value = False
