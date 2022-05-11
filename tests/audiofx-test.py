# Raspberry Pi Pico (RP2040) MIDI Drum Machine - Audio FX Text
# 2022 DCooper Dalrymple - me@dcdalrymple.com
# GPL v2 License
# Version 1.0

import time
import board

from digitalio import DigitalInOut
from digitalio import Direction

from audiocore import WaveFile
import audiomixer
import audiofx
from audiopwmio import PWMAudioOut

AUDIO_BUFFER_SIZE = 1024
AUDIO_RATE        = 22050
AUDIO_CHANNELS    = 2
AUDIO_BITS        = 16

TEST_RATE         = 0.01
TEST_ITERATIONS   = 500

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Wait for USB to stabilize
time.sleep(0.5)

print("RPi Pico Drum - Audio FX Test")
print("Version 1.0")
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

stereo = WaveFile(open("samples/stereo.wav", "rb")) # 22050, 16-bit, stereo wav file

print("\n:: Low Pass Filter ::")
lpf = audiofx.Filter(
    type=audiofx.FilterType.LPF,
    sample_rate=AUDIO_RATE,
    channel_count=AUDIO_CHANNELS,
    bits_per_sample=AUDIO_BITS,
    samples_signed=True
)
lpf.play(mixer)
audio.play(lpf)
mixer.voice[0].play(stereo, loop=True)
for j in range(4):
    lpf.resonance = j / 4
    print("Sweeping cutoff at resonance ", lpf.resonance)
    for i in range(iterations):
        lpf.cutoff = i / iterations
        time.sleep(rate)
mixer.voice[0].stop()
audio.stop()
lpf.stop()

print("\n:: Testing complete ::")
led.value = False
