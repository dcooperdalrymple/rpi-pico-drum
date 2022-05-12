/**
 * Package: rpi-pico-drum
 * File: coretalk.cpp
 * Title: Multi-core Communication
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include "coretalk.hpp"

core_talk_callback_t CoreTalk::cb[CORE_NUM] = {NULL, NULL};
