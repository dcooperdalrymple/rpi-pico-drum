/**
 * RPi Pico Drum Machine
 * 2022 D Cooper Dalrymple - me@dcdalrymple.com
 * GPL v3 License
 *
 * Package: rpi-pico-drum
 * File: main.cpp
 * Title: Main
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pico/stdlib.h"
#include "pico/binary_info.h"

#include "ss_oled.hpp"

#include "src/hw_config.h"

#include "src/config.hpp"
#include "src/display.hpp"
#include "src/rotary.hpp"
#include "src/coretalk.hpp"

static CoreTalk coretalk;

// Secondary Core (display/rotary)

static Display display;
static Rotary menu_rotary(MENU_CLK, MENU_SW);
static Rotary mod_rotary(MOD_CLK, MOD_SW);

void interface_menu_rotary_handler(uint8_t event) {
    switch (event) {
        case ROTARY_CW:
            if (menu_rotary.get_rotation() >= ROTARY_BOUNCE) {
                menu_rotary.set_rotation(0);
                // do right
            }
            break;
        case ROTARY_CCW:
            if (menu_rotary.get_rotation() <= -ROTARY_BOUNCE) {
                menu_rotary.set_rotation(0);
                // do left
            }
            break;
        case ROTARY_PRESS:
            break;
        case ROTARY_RELEASE:
            // do click
            break;
    }
}

void interface_mod_rotary_handler(uint8_t event) {
    switch (event) {
        case ROTARY_CW:
            if (mod_rotary.get_rotation() >= ROTARY_BOUNCE) {
                mod_rotary.set_rotation(0);
                // do right
            }
            break;
        case ROTARY_CCW:
            if (mod_rotary.get_rotation() <= -ROTARY_BOUNCE) {
                mod_rotary.set_rotation(0);
                // do left
            }
            break;
        case ROTARY_PRESS:
            break;
        case ROTARY_RELEASE:
            // do click
            break;
    }
}

void interface_core_handler(uint32_t event, uint32_t value) {
    switch (event) {
        case CORE_POKE:
            break;
        case CORE_DATA:
            break;
    }
}

void interface_core() {
    // Blocking handshake with core0
    if (!coretalk.handshake()) return;

    coretalk.setup();
    coretalk.set_callback(&interface_core_handler);
    menu_rotary.set_callback(&interface_menu_rotary_handler);
    mod_rotary.set_callback(&interface_mod_rotary_handler);
}

// Main Core (Audio Processing)

void audio_core_handler(uint32_t event, uint32_t value) {
    switch (event) {
        case CORE_POKE:
            break;
        case CORE_DATA:
            break;
    }
}

int main() {
    stdio_init_all();

    // Setup core1 and do blocking handshake
    multicore_launch_core1(interface_core);
    if (!coretalk.handshake()) return 1;

    coretalk.setup();
    coretalk.set_callback(&audio_core_handler);

    absolute_time_t now_timestamp = nil_time;
    while (1) {
        now_timestamp = get_absolute_time();
    }

    return 0;
}
