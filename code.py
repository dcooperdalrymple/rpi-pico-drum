# Raspberry Pi Pico (RP2040) MIDI Drum Machine
# 2022 DCooper Dalrymple - me@dcdalrymple.com
# GPL v2 License
# Version 0.1.0

import sys
import os
import gc
import time
import board

import json
import sdcardio
import storage

from digitalio import DigitalInOut
from digitalio import Direction

from audiocore import RawSample
from audiocore import WaveFile
import audiomixer
from audiopwmio import PWMAudioOut

import busio
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.program_change import ProgramChange

MAX_SAMPLES       = 16

MIDI_CHANNEL      = 10
MIDI_THRU         = False

AUDIO_BUFFER_SIZE = 1024
AUDIO_RATE        = 22050
AUDIO_CHANNELS    = 2
AUDIO_BITS        = 16
AUDIO_OUTPUT      = "pwm"

CONFIG            = "config.json"
SD_MOUNT          = "/sd"
SD_CONFIG         = "config.json"

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Wait for USB to stabilize
time.sleep(0.5)

print("RPi Pico Drum")
print("Version 0.1.0")
print("Cooper Dalrymple, 2022")
print("https://dcdalrymple.com/rpi-pico-drum/")

class Sample:
    def __init__(self, index):
        self.index = index

        self.note = 0
        self.level = 1.0
        self.minLevel = 0.0
        self.pan = 0.5
        self.loop = False
        self.stopNoteOff = False

    def load(self, data):
        if not "file" in data:
            return False

        print("Loading Sample:", data["file"])

        if hasattr(self, "wave"):
            self.unload()

        self.data = data
        self.note = data["note"] if data["note"] else 0
        self.level = data["level"] if data["level"] else 1.0
        self.minLevel = data["minLevel"] if data["minLevel"] else 0.0
        self.pan = data["pan"] if data["pan"] else 0.5
        self.loop = data["loop"] if data["loop"] else False
        self.stopNoteOff = data["noteOff"] if data["noteOff"] else False

        self.file = open(data["file"], "rb");
        self.wave = WaveFile(self.file)
        if self.wave == False:
            self.unload()

    def noteOn(self, velocity=1.0):
        if not self.wave:
            return False
        if velocity == 0.0:
            self.noteOff()
        else:
            mixer.voice[self.index].play(self.wave, loop=self.loop)
            mixer.voice[self.index].level = velocity * (self.level - self.minLevel) + self.minLevel
        return True

    def noteOff(self):
        if self.stopNoteOff:
            if mixer.voice[self.index].playing:
                mixer.voice[self.index].stop()
            mixer.voice[self.index].level = 0.0
        return True

    def unload(self):
        self.noteOff()
        if self.wave:
            self.wave.deinit()
            del self.wave
        if self.data:
            del self.data
        gc.collect()

class Patch:
    def __init__(self):
        self.samples = [None for i in range(MAX_SAMPLES)]
        for i in range(MAX_SAMPLES):
            self.samples[i] = Sample(i)

    def load(self, data):
        if not "samples" in data:
            return False

        if hasattr(self, "data"):
            self.unload()
        self.data = data

        for i in range(min(MAX_SAMPLES, len(self.data["samples"]))):
            self.samples[i].load(self.data["samples"][i])

    def unload(self):
        for i in range(MAX_SAMPLES):
            self.samples[i].unload()
        if self.data:
            del self.data
        gc.collect()

    def noteOn(self, note, velocity):
        for i in range(min(MAX_SAMPLES, len(self.data["samples"]))):
            if self.samples[i].note == note:
                return self.samples[i].noteOn(velocity)
        return False

    def noteOff(self, note):
        for i in range(min(MAX_SAMPLES, len(self.data["samples"]))):
            if self.samples[i].note == note:
                return self.samples[i].noteOff()
        return False

class Config:
    def __init__(self, file=None):
        self.data = dict()
        if file != None:
            self.readFile(file)

    def mergeData(self, data, target=None):
        if target == None:
            target = self.data
        for key, value in data.items():
            if isinstance(value, dict):
                if not key in target:
                    target[key] = dict()
                target[key] = self.mergeData(value, target[key])
            elif isinstance(value, list):
                if not key in target:
                    target[key] = []
                target[key].extend(value)
            else:
                target[key] = value
        return target

    def readFile(self, filename, file_prefix=""):
        file = open(filename, "r")
        data = json.loads(file.read())

        # Filename prefix
        if len(file_prefix) > 0 and "patches" in data and len(data["patches"]) > 0:
            for i, patch in enumerate(data["patches"]):
                if "samples" in patch and len(patch["samples"]) > 0:
                    for j, sample in enumerate(patch["samples"]):
                        if "file" in sample and len(sample["file"]) > 0:
                            data["patches"][i]["samples"][j]["file"] = file_prefix + sample["file"]

        self.mergeData(data)

        del data
        file.close()
        del file
        gc.collect()

    def getData(self, default, group, key=None):
        if not group in self.data or (key != None and not key in self.data[group]):
            return default
        if key != None:
            return self.data[group][key]
        else:
            return self.data[group]

    def getPatch(self, index):
        if not "patches" in self.data or index >= len(self.data["patches"]):
            return False
        return self.data["patches"][index]

    def getProgram(self, num):
        for i in range(len(self.data["patches"])):
            if self.data["patches"][i]["program"] == num:
                return self.data["patches"][i]
        return False

    def getAudioBufferSize(self):
        return self.getData(AUDIO_BUFFER_SIZE, "audio", "bufferSize")
    def getAudioRate(self):
        return self.getData(AUDIO_RATE, "audio", "rate")
    def getAudioOutput(self):
        return self.getData(AUDIO_OUTPUT, "audio", "output")

    def getMidiChannel(self):
        return self.getData(MIDI_CHANNEL, "midi", "channel")
    def getMidiThru(self):
        return self.getData(MIDI_THRU, "midi", "thru")

print(":: Reading Flash Memory ::")
config = Config(CONFIG)

print(":: Reading SD Card ::")
spi = busio.SPI(board.GP10, board.GP11, board.GP8)
try:
    sd = sdcardio.SDCard(spi, board.GP9)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, SD_MOUNT)
    config.readFile(SD_MOUNT + "/" + SD_CONFIG, SD_MOUNT + "/")

    if not "patches" in config.data or len(config.data["patches"]) == 0:
        print("No patches or samples provided. Please see repository for config format.")
        sys.exit()
except:
    print("No SD card detected or invalid file system format. SD card must be formatted as FAT32.")

print("Patches:", len(config.data["patches"]))

print(":: Initializing Audio ::")

mixer = audiomixer.Mixer(
    voice_count=MAX_SAMPLES,
    buffer_size=config.getAudioBufferSize(),
    sample_rate=config.getAudioRate(),
    channel_count=AUDIO_CHANNELS,
    bits_per_sample=AUDIO_BITS,
    samples_signed=True
)

audio = None
if config.getAudioOutput() == "pwm":
    audio = PWMAudioOut(
        left_channel=board.GP26,
        right_channel=board.GP27
    )
elif config.getAudioOutput() == "i2s":
    pass
if audio == None:
    print("Invalid audio output type. Please see repository for valid output types.")
    sys.exit()
audio.play(mixer)

print("Buffer Size:", config.getAudioBufferSize())
print("Sample Rate:", config.getAudioRate())
print("Channels:", AUDIO_CHANNELS)
print("Bits:", AUDIO_BITS)
print("Output:", config.getAudioOutput())

print(":: Initializing Midi ::")
uart = busio.UART(
    tx=board.GP4,
    rx=board.GP5,
    baudrate=31250,
    timeout=0.001
)
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=config.getMidiChannel()-1,
    out_channel=config.getMidiChannel()-1,
    debug=False
)
print("Channel:", midi.in_channel+1)

print(":: Initializing Interface ::")

print(":: Loading Default Patch ::")
patch = Patch()
patch.load(config.getPatch(0))

print(":: Initialization Complete ::")
led.value = False

while True:
    while True:
        msg_in = midi.receive()
        if msg_in == None:
            break

        if config.getMidiThru():
            midi.send(msg_in)

        if isinstance(msg_in, NoteOn):
            patch.noteOn(msg_in.note, msg_in.velocity / 127.0)
        elif isinstance(msg_in, NoteOff):
            patch.noteOff(msg_in.note)
        elif isinstance(msg_in, ProgramChange):
            patch.load(config.getProgram(msg_in.patch))

    playing = False
    for i in range(MAX_SAMPLES):
        if mixer.voice[i].playing:
            playing = True
            break
    led.value = playing
