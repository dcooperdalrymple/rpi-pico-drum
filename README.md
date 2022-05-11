# rpi-pico-drum
MIDI Drum Machine using the RP2040.

## Specifications

* Maximum 8 samples per patch, can play simultaneously
* Multiple supported audio sample rates. Ie: 22050, 44100
* Uses built-in flash memory of Pico and supports external SD card for configuration and sample storage.
* Hardware midi uart with thru support.
* Velocity sensitivity, pan, loop, etc defined per sample in JSON configuration file.
* I2S or PWM audio hardware options.
* Simple OLED display and rotary control.

## Installation

1. Configure: `cmake -B build -S .`
2. Compile/Build: `make -C build`
3. Write: Hold BOOTSEL button on Pico, plug it in via USB, and release BOOTSEL. Copy and paste `rpi-pico-drum.uf2` into RPI-RP2 drive.
4. Format your MicroSD card as FAT32 and copy `config.json` into the root directory.

## Configuration

### Sample Wave Files

Samples can be stored wherever you'd like within your MicroSD flash storage (formatted as FAT32), but it's generally recommended to keep your patches within individual folders which contain all the samples for that patch.

In order to convert your samples into the appropriate format, use the following command:

`sox %SAMPLE%.wav -b %BITS% -c %CHANNELS% -r %SAMPLERATE% %SAMPLE%.wav`

With the default settings, this would look something like `sox kick.wav -b 16 -c 1 -r 44100 kick.wav`. Make sure that all of your samples respect the same audio configuration or else runtime errors may occur. If you don't have `sox` already installed, you can do so on Debian/Ubuntu installations by running the command `sudo apt install sox`.

### JSON Config

All of the settings of the device and samples/patches are configured using the config.json file stored in the root directory of your MicroSD card. If you're not familiar with JSON, it's structure can be very strict and cause errors if it's not formatted properly. I recommending reading up on it [here](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON).

The first patch located in the `"patches"` array is loaded by default when the Pico boots up. You can add more patches here following the same format as the "Default" patch which will be loaded sequentially.

* The `"program"` setting is used for incoming Midi Program Change messages.
* The `"note"` settings for each sample in the `"samples"` array are used for incoming Midi Note messages to trigger each sample.

## Planned Features

* Real-time effects including LPF, HPF, BPF, reverb, phase, chorus, bit-crush, etc.
* Pitch shifting and note ranges.
