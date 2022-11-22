/**
 * Package: rpi-pico-drum
 * File: audio.hpp
 * Title: Audio Driver Interface
 * Version: 0.2.0
 * Since: 0.2.0
 */

#pragma once

#define AUDIO_VOICES        8

#define AUDIO_OUTPUT_PWM    0
#define AUDIO_OUTPUT_I2S    1

// Default Configuration
#define AUDIO_BUFFER_SIZE   1024
#define AUDIO_RATE          22050
#define AUDIO_CHANNELS      2
#define AUDIO_BITS          16
#define AUDIO_VOLUME        1.0

#include "pico/audio_i2s.h"
#include "pico/audio_pwm.h"
