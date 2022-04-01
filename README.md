# rpi-pico-drum
MIDI Drum Machine using the RP2040 &amp; CircuitPython.

## Specifications

* Maximum 8 samples per patch, can play simultaneously
* Multiple supported audio sample rates. Ie: 22050, 44100
* Uses built-in flash memory of Pico. 2MB maximum sample storage.
* Hardware midi uart with thru support.
* Velocity sensitivity, pan, loop, etc defined per sample in JSON configuration file.
* I2S or PWM audio hardware options.
* Simple OLED display and rotary control.

## Installation

1. Download and install CircuitPython bootloader: [instructions & UF2 file](https://circuitpython.org/board/raspberry_pi_pico/).
1. Add adafruit_midi library to `/lib/adafruit_midi` in CircuitPython storage: [GitHub Repository](https://github.com/adafruit/Adafruit_CircuitPython_MIDI).
1. Copy `code.py`, `config.json`, and `default` folder of samples into root directory of CircuitPython storage.
1. Connect your midi device configured for channel 10 and give it a shot!

## Configuration

### Sample Wave Files

Samples can be stored wherever you'd like within the Pico's storage, but it's generally recommended to keep your patches within individual folders which contain all the samples for that patch.

In order to convert your samples into the appropriate format, use the following command:

`sox %SAMPLE%.wav -b %BITS% -c %CHANNELS% -r %SAMPLERATE% %SAMPLE%.wav`

With the default settings, this would look something like `sox kick.wav -b 16 -c 1 -r 44100 kick.wav`. Make sure that all of your samples respect the same audio configuration or else runtime errors may occur. If you don't have `sox` already installed, you can do so on Debian/Ubuntu installations by running the command `sudo apt install sox`.

### JSON Config

All of the settings of the device and samples/patches are configured using the config.json file stored in the root directory of CircuitPython. If you're not familiar with JSON, it's structure can be very strict and cause errors if it's not formatted properly. I recommending reading up on it [here](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON).

The first patch located in the `"patches"` array is loaded by default when the Pico boots up. You can add more patches here following the same format as the "Default" patch which will be loaded sequentially.

* The `"program"` setting is used for incoming Midi Program Change messages.
* The `"note"` settings for each sample in the `"samples"` array are used for incoming Midi Note messages to trigger each sample.

## Notes

* Panning is not currently supported but will be coming very soon. You can ignore sample pan settings for now.
* Pitch shifting and note ranges is not currently supported but may come in a future release.
