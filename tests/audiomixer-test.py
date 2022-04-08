# Raspberry Pi Pico (RP2040) MIDI Drum Machine - Audio Mixer Text
# 2022 DCooper Dalrymple - me@dcdalrymple.com
# GPL v2 License
# Version 1.0

import time
import board

from digitalio import DigitalInOut
from digitalio import Direction

from audiocore import WaveFile
import audiomixer
from audiopwmio import PWMAudioOut

AUDIO_BUFFER_SIZE = 1024
AUDIO_RATE        = 22050
AUDIO_CHANNELS    = 2
AUDIO_BITS        = 16

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Wait for USB to stabilize
time.sleep(0.5)

print("RPi Pico Drum - Mono/Stereo & Pan Test")
print("Version 0.1.0")
print("Cooper Dalrymple, 2022")
print("https://dcdalrymple.com/rpi-pico-drum/")

audio = PWMAudioOut(
    left_channel=board.GP26,
    right_channel=board.GP27
)
mixer = audiomixer.Mixer(
    voice_count=2,
    buffer_size=AUDIO_BUFFER_SIZE,
    sample_rate=AUDIO_RATE,
    channel_count=AUDIO_CHANNELS,
    bits_per_sample=AUDIO_BITS,
    samples_signed=True
)
audio.play(mixer)

mono = WaveFile(open("samples/mono.wav", "rb")) # 22050, 16-bit, mono wav file
stereo = WaveFile(open("samples/stereo.wav", "rb")) # 22050, 16-bit, stereo wav file

rate = 0.01
iterations = 500

print("\n:: Mono to stereo conversion ::")
mixer.voice[0].level = 1
mixer.voice[0].pan = 0
print("Stereo")
mixer.voice[0].play(stereo, loop=True)
time.sleep(2)
mixer.voice[0].stop()
print("Mono => Stereo")
mixer.voice[0].play(mono, loop=True)
time.sleep(2)
mixer.voice[0].stop()

print("\n:: Stereo pan ::")
mixer.voice[0].play(stereo, loop=True)
print("Stereo left to right")
for i in range(iterations):
    mixer.voice[0].pan = i / iterations * 2 - 1
    time.sleep(rate)
print("Stereo right to left")
for i in range(iterations):
    mixer.voice[0].pan = 1 - i / iterations * 2
    time.sleep(rate)
mixer.voice[0].stop()

print("\n:: Mono pan ::")
mixer.voice[0].play(mono, loop=True)
print("Mono left to right")
for i in range(iterations):
    mixer.voice[0].pan = i / iterations * 2 - 1
    time.sleep(rate)
print("Mono right to left")
for i in range(iterations):
    mixer.voice[0].pan = 1 - i / iterations * 2
    time.sleep(rate)
mixer.voice[0].stop()

print("\n:: Pan & level blend ::")
mixer.voice[0].level = 0.5
mixer.voice[0].pan = 0
mixer.voice[0].play(stereo, loop=True)
mixer.voice[1].play(mono, loop=True)
print("Fade mono in and pan left to right (stereo played beneath at half level)")
for i in range(iterations):
    mixer.voice[1].level = i / iterations
    mixer.voice[1].pan = i / iterations * 2 - 1
    time.sleep(rate)
print("Cross pan stereo (left to right) and mono (right to left)")
mixer.voice[0].level = 1.0
mixer.voice[1].level = 1.0
for i in range(iterations):
    mixer.voice[0].pan = i / iterations * 2 - 1
    mixer.voice[1].pan = 1 - i / iterations * 2
    time.sleep(rate)
mixer.voice[0].stop()
mixer.voice[1].stop()

print("\n:: Testing complete ::")
led.value = False
