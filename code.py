"""
RPi Pico Drum Machine
2022 D Cooper Dalrymple - me@dcdalrymple.com
GPL v2 License

File: code.py
Title: Main Script
Version: 0.1.0
Since: 0.1.0
"""

import sys
import os
import gc
import time
import board

import json
import sdcardio
import storage

from digitalio import DigitalInOut, Direction, Pull
from busio import I2C, SPI, UART
from rotaryio import IncrementalEncoder

from adafruit_neotrellis.neotrellis import NeoTrellis

import menu

from audiocore import WaveFile
import audiomixer
from audiopwmio import PWMAudioOut

from audiobusio import I2SOut
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.program_change import ProgramChange

# Program Constants

MAX_SAMPLES       = 256
MAX_VOICES        = 8

MIDI_CHANNEL      = 10
MIDI_THRU         = False

AUDIO_BUFFER_SIZE = 1024
AUDIO_RATE        = 22050
AUDIO_CHANNELS    = 2
AUDIO_BITS        = 16
AUDIO_OUTPUT      = "i2s" # "pwm" or "i2s"
AUDIO_VOLUME      = 1.0

CONFIG            = "config.json"
SD_MOUNT          = "/sd"
SD_CONFIG         = "config.json"

MAX_PAD           = 16
PAD_VELOCITY      = 127

DISPLAY_ADDRESS   = 0x3c
DISPLAY_WIDTH     = 128
DISPLAY_HEIGHT    = 64

# Color Constants

COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 150, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_PURPLE = (180, 0, 255)
COLOR_GRAY = (150, 150, 150)
COLOR_WHITE = (255, 255, 255)

COLOR_OFF = COLOR_BLACK
COLOR_DEFAULT = COLOR_RED
COLOR_ACTIVE = COLOR_WHITE
COLOR_MIDI = COLOR_GRAY

def getColor(name):
    name = name.lower()
    if name == "black":
        return COLOR_BLACK
    elif name == "red":
        return COLOR_RED
    elif name == "yellow":
        return COLOR_YELLOW
    elif name == "green":
        return COLOR_GREEN
    elif name == "cyan":
        return COLOR_CYAN
    elif name == "blue":
        return COLOR_BLUE
    elif name == "purple":
        return COLOR_PURPLE
    elif name == "gray":
        return COLOR_GRAY
    elif name == "white":
        return COLOR_WHITE
    else:
        return COLOR_DEFAULT

# Initialize status LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Initialize NeoTrellis I2C RGB 4x4 Button Pad
trellis_i2c = I2C(scl=board.GP19, sda=board.GP18)
trellis = NeoTrellis(trellis_i2c)
trellis_buffer = [COLOR_OFF for i in range(MAX_PAD)]
for i in range(MAX_PAD):
    trellis.pixels[i] = trellis_buffer[i]
    time.sleep(0.05)

# Initialize Menu Display and Encoder
menu.release_displays()
display_i2c = I2C(scl=board.GP21, sda=board.GP20)
display_menu = menu.Menu(
    i2c=display_i2c,
    encoder_pin_a=board.GP12,
    encoder_pin_b=board.GP13,
    button_pin=board.GP7,
    address=DISPLAY_ADDRESS,
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT
)

# Initialize SFX Mod Encoder
mod_encoder = IncrementalEncoder(board.GP26, board.GP27)
mod_button = DigitalInOut(board.GP28)
mod_button.direction = Direction.INPUT
mod_button.pull = Pull.UP

# Initialization Screen
display_menu.splash_image()
display_menu.splash_message("Version 0.1.0")

# Wait for USB to stabilize
time.sleep(0.5)

# Serial Header
print("RPi Pico Drum Machine\nVersion 0.1.0\nCooper Dalrymple, 2022\nhttps://dcdalrymple.com/rpi-pico-drum/")

# Class Definitions

class Sample:
    def __init__(self, index, data = None):
        self.index = index

        self.note = 0
        self.pad = -1
        self.color = COLOR_DEFAULT
        self.level = 1.0
        self.minLevel = 0.0
        self.pan = 0.0
        self.loop = False
        self.stopNoteOff = False

        self.voice = -1

        if data != None:
            self.load(data)

    def load(self, data):
        if not "file" in data:
            return False

        print("Loading Sample:", data["file"])

        if hasattr(self, "wave"):
            self.unload()

        self.data = data
        self.note = data["note"] if "note" in data else 0
        self.pad = data["pad"] if "pad" in data else -1
        self.color = getColor(data["color"]) if "color" in data else COLOR_DEFAULT
        self.level = data["level"] if "level" in data else 1.0
        self.minLevel = data["minLevel"] if "minLevel" in data else 0.0
        self.pan = data["pan"] if "pad" in data else 0.0
        self.loop = data["loop"] if "loop" in data else False
        self.stopNoteOff = data["noteOff"] if "noteOff" in data else False

        self.file = open(data["file"], "rb");
        self.wave = WaveFile(self.file)
        if self.wave == False:
            self.unload()
            return False

        return True

    def noteOn(self, velocity=1.0):
        if not self.wave:
            return False
        if velocity <= 0.0:
            self.noteOff()
        else:
            self.stop()
            for i in range(MAX_VOICES):
                if mixer.voice[i].playing:
                    continue
                self.voice = i
                mixer.voice[i].play(self.wave, loop=self.loop)
                mixer.voice[i].level = min(1.0, max(0.0, velocity * (self.level - self.minLevel) + self.minLevel) * config.getAudioVolume())
                mixer.voice[i].pan = max(-1.0, min(1.0, self.pan))
                return True
        return False

    def noteOff(self):
        if self.stopNoteOff:
            return self.stop()
        return True

    def stop(self):
        if self.voice < 0:
            return False
        if mixer.voice[self.voice].playing:
            mixer.voice[self.voice].stop()
        mixer.voice[self.voice].level = 0.0
        mixer.voice[self.voice].pan = 0.0
        self.voice = -1
        return True

    def unload(self):
        self.noteOff()
        if self.wave:
            self.wave.deinit()
            del self.wave
        if self.file:
            self.file.close()
            del self.file
        if self.data:
            del self.data
        gc.collect()

class Patch:
    def __init__(self):
        pass

    def load(self, data):
        if not "samples" in data:
            return False

        if hasattr(self, "data") or hasattr(self, "samples"):
            self.unload()
        self.data = data

        self.samples = []
        for i in range(min(MAX_SAMPLES, len(self.data["samples"]))):
            self.samples.append(Sample(i, self.data["samples"][i]))

        for i in range(MAX_PAD):
            sample = self.getPad(i)
            if sample:
                setTrellisBuffer(i, tuple(int(c/2) for c in sample.color), True)
            else:
                setTrellisBuffer(i, COLOR_OFF, True)

    def unload(self):
        if hasattr(self, "samples"):
            for i in range(len(self.samples)):
                self.samples[i].unload()
            del self.samples
        if hasattr(self, "data") and self.data:
            del self.data
        gc.collect()

    def noteOn(self, note, velocity):
        sample = self.getNote(note)
        if sample:
            return sample.noteOn(velocity)
        return False
    def noteOff(self, note):
        sample = self.getNote(note)
        if sample:
            return sample.noteOff()
        return False
    def getNote(self, note):
        if not hasattr(self, "data") or not self.data or not self.data["samples"]:
            return False
        for i in range(min(MAX_SAMPLES, len(self.data["samples"]))):
            if self.samples[i].note == note:
                return self.samples[i]
        return False

    def padOn(self, pad, velocity=PAD_VELOCITY):
        sample = self.getPad(pad)
        if sample:
            return sample.noteOn(velocity)
        return False
    def padOff(self, pad):
        sample = self.getPad(pad)
        if sample:
            return sample.noteOff()
        return False
    def getPad(self, pad):
        if not hasattr(self, "data") or not self.data or not self.data["samples"]:
            return False
        for i in range(len(self.data["samples"])):
            if self.samples[i].pad == pad:
                return self.samples[i]
        return False

    def getVoice(self, voice):
        if not hasattr(self, "data") or not self.data or not self.data["samples"]:
            return False
        for i in range(len(self.data["samples"])):
            if self.samples[i].voice == voice:
                return self.samples[i]
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
    def setData(self, group, key, value):
        if not group in self.data or not key in self.data[group]:
            return False
        self.data[group][key] = value
        return True

    def getPatch(self, index):
        if not "patches" in self.data or index >= len(self.data["patches"]):
            return False
        return self.data["patches"][index]
    def getSelectorItems(self):
        items = list()

        if not "patches" in self.data or len(self.data["patches"]) == 0:
            return items

        for i in range(len(self.data["patches"])):
            if "name" in self.data["patches"][i]:
                items.append(self.data["patches"][i]["name"])
            else:
                items.append(str(i))
        return items

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

    def getAudioVolume(self):
        return self.getData(AUDIO_VOLUME, "audio", "volume")
    def setAudioVolume(self, value):
        if value < 0 or value > 1:
            return False
        return self.setData("audio", "volume", value)

    def getMidiChannel(self):
        return self.getData(MIDI_CHANNEL, "midi", "channel")
    def setMidiChannel(self, value):
        if type(value) != type(1) or value < 1 or value > 16:
            return False
        return self.setData("midi", "channel", value)

    def getMidiThru(self):
        return self.getData(MIDI_THRU, "midi", "thru")
    def setMidiThru(self, value):
        if type(value) != type(True):
            return False
        return self.setData("midi", "thru", value)

def handleTrellis(event):
    if event.edge == NeoTrellis.EDGE_RISING:
        patch.padOn(event.number)
        trellis.pixels[event.number] = COLOR_ACTIVE
    elif event.edge == NeoTrellis.EDGE_FALLING:
        patch.padOff(event.number)
        trellis.pixels[event.number] = trellis_buffer[event.number]
def setTrellisBuffer(pad, color, set=False):
    if trellis.pixels[pad] == trellis_buffer[pad]:
        trellis.pixel[pad] = color
    trellis_buffer[pad] = color
    if set:
        trellis.pixels[pad] = trellis_buffer[pad]

display_menu.splash_message("Reading Flash Memory")
print(":: Reading Flash Memory ::")
config = Config()
try:
    config.readFile(CONFIG)
except:
    print("No internal config file detected.")

display_menu.splash_message("Reading SD Card")
print(":: Reading SD Card ::")
spi = SPI(board.GP10, board.GP11, board.GP8)
try:
    sd = sdcardio.SDCard(spi, board.GP9)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, SD_MOUNT)
    config.readFile(SD_MOUNT + "/" + SD_CONFIG, SD_MOUNT + "/")

    if not "patches" in config.data or len(config.data["patches"]) == 0:
        display_menu.splash_message("No Patches Found")
        print("No patches or samples provided. Please see repository for config format.")
        sys.exit()
except:
    print("No SD card detected or invalid file system format. SD card must be formatted as FAT32.")

print("Patches:", len(config.data["patches"]))

display_menu.splash_message("Initializing Audio")
print(":: Initializing Audio ::")

mixer = audiomixer.Mixer(
    voice_count=MAX_VOICES,
    buffer_size=config.getAudioBufferSize(),
    sample_rate=config.getAudioRate(),
    channel_count=AUDIO_CHANNELS,
    bits_per_sample=AUDIO_BITS,
    samples_signed=True
)

audio = None
if config.getAudioOutput() == "pwm":
    audio = PWMAudioOut(
        left_channel=board.GP16,
        right_channel=board.GP17
    )
elif config.getAudioOutput() == "i2s":
    audio = I2SOut(board.GP0, board.GP1, board.GP2)
if audio == None:
    display_menu.splash_message("Invalid Audio Output")
    print("Invalid audio output type. Please see repository for valid output types.")
    sys.exit()
audio.play(mixer)

print("Buffer Size:", config.getAudioBufferSize())
print("Sample Rate:", config.getAudioRate())
print("Channels:", AUDIO_CHANNELS)
print("Bits:", AUDIO_BITS)
print("Output:", config.getAudioOutput())

display_menu.splash_message("Initializing Midi")
print(":: Initializing Midi ::")
uart = UART(
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

display_menu.splash_message("Initializing Interface")
print(":: Initializing Interface ::")

print("Activating NeoTrellis Keys")
for i in range(MAX_PAD):
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    trellis.callbacks[i] = handleTrellis
    trellis.pixels[i] = COLOR_PURPLE
    time.sleep(0.05)
for i in range(MAX_PAD):
    trellis.pixels[i] = COLOR_OFF
    time.sleep(0.05)

display_menu.splash_message("Loading Default")
print(":: Loading Default Patch ::")
patch = Patch()
patch.load(config.getPatch(0))

display_menu.splash_message("Initialization Complete")
print(":: Initialization Complete ::")
led.value = False

# Setup Display Menu
def menu_update(item):
    if item.get_key() == "patch":
        current_patch = config.getPatch(item.get())
        patch.load(current_patch)
        print("Patch:", current_patch["name"])
    elif item.get_key() == "volume":
        config.setAudioVolume(item.get() / 100.0)
    elif item.get_key() == "midi_channel":
        config.setMidiChannel(item.get())
        midi.in_channel = config.getMidiChannel()-1
        midi.out_channel = config.getMidiChannel()-1
        print("Midi Channel:", config.getMidiChannel())
    elif item.get_key() == "midi_thru":
        config.setMidiThru(item.get())
        print("Midi Thru:", config.getMidiThru())

display_menu.setup(menu_update)
patch_item = display_menu.find_item("patch")
if patch_item != None:
    patch_item.set_items(config.getSelectorItems())
    display_menu.draw()

while True:
    # trigger callbacks
    trellis.sync()

    # Update menu
    display_menu.update()

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
    for i in range(MAX_VOICES):
        if mixer.voice[i].playing:
            playing = True
            break
    led.value = playing

    for i in range(MAX_PAD):
        sample = patch.getPad(i)
        if not sample or sample.voice < 0:
            continue
        if mixer.voice[sample.voice].playing:
            setTrellisBuffer(i, sample.color)
        else:
            setTrellisBuffer(i, tuple(int(c/2) for c in sample.color))
            sample.stop()

    time.sleep(0.02)

print("\n:: Program Shutting Down ::")
display_menu.deinit()
mod_encoder.deinit()
