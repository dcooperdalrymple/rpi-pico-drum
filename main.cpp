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

#include "neotrellis.hpp"
#include "ss_oled.hpp"
#include "hw_config.h"

#include "hw_config.hpp"
#include "storage.hpp"
#include "config.hpp"
#include "display.hpp"
#include "rotary.hpp"
#include "coretalk.hpp"

static CoreTalk coretalk;

// Secondary Core (display/rotary)

static Storage storage(sd_get_by_num(0));
static Config config(&storage);
static NeoTrellis trellis(TRELLIS_I2C, TRELLIS_SDA, TRELLIS_SCL);
static Display display;
static Rotary menu_rotary(MENU_CLK, MENU_SW);
static Rotary mod_rotary(MOD_CLK, MOD_SW);

void interface_menu_rotary_handler(uint8_t event) {
    switch (event) {
        case ROTARY_CW:
            if (menu_rotary.get_rotation() >= ROTARY_BOUNCE) {
                menu_rotary.set_rotation(0);
                // do right
                display.splash_message((char *)"Menu Right");
            }
            break;
        case ROTARY_CCW:
            if (menu_rotary.get_rotation() <= -ROTARY_BOUNCE) {
                menu_rotary.set_rotation(0);
                // do left
                display.splash_message((char *)"Menu Left");
            }
            break;
        case ROTARY_PRESS:
            display.splash_message((char *)"Menu Press");
            break;
        case ROTARY_RELEASE:
            // do click
            display.splash_message((char *)"Menu Release");
            break;
    }
}

void interface_mod_rotary_handler(uint8_t event) {
    switch (event) {
        case ROTARY_CW:
            if (mod_rotary.get_rotation() >= ROTARY_BOUNCE) {
                mod_rotary.set_rotation(0);
                // do right
                display.splash_message((char *)"Mod Right");
            }
            break;
        case ROTARY_CCW:
            if (mod_rotary.get_rotation() <= -ROTARY_BOUNCE) {
                mod_rotary.set_rotation(0);
                // do left
                display.splash_message((char *)"Mod Left");
            }
            break;
        case ROTARY_PRESS:
            display.splash_message((char *)"Mod Press");
            break;
        case ROTARY_RELEASE:
            // do click
            display.splash_message((char *)"Mod Release");
            break;
    }
}

void interface_keypad_handler(uint8_t key, Keypad::Edge edge) {
    if (edge == Keypad::Edge::RISING) {

    } else {

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
    uint8_t i;

    // Initialize LED and turn on while device is initializing
    gpio_init(LED);
    gpio_set_dir(LED, GPIO_OUT);
    gpio_put(LED, 1);

    // Display
    display.init();
    display.splash();

    // NeoTrellis
    display.splash_message((char *)"Configuring NeoTrellis");
    trellis.init();
    for (i = 0; i < 16; i++) {
        trellis.pixels.set(i, COLOR_WHITE);
        trellis.pixels.show();
        sleep_ms(20);
    }
    for (i = 0; i < 16; i++) {
        trellis.pixels.set(i, COLOR_BLACK);
        trellis.pixels.show();
        sleep_ms(20);
    }

    // SD Storage
    display.splash_message((char *)"Initializing SD FAT storage");
    if (!storage.init()) {
        display.splash_message((char *)"Failed to initialize storage");
        return;
    }

    // Config
    display.splash_message((char *)"Reading configuration");
    if (!config.init()) {
        display.splash_message((char *)"Invalid configuration data");
        return;
    }

    // Blocking handshake with core0
    display.splash_message((char *)"Waiting for audio core");
    if (!coretalk.handshake()) return;

    display.clear();
    gpio_put(LED, 0);

    coretalk.setup();
    coretalk.set_callback(&interface_core_handler);
    menu_rotary.set_callback(&interface_menu_rotary_handler);
    mod_rotary.set_callback(&interface_mod_rotary_handler);
    trellis.keypad.set_callback(&interface_keypad_handler);

    while (true) {
        sleep_ms(1000);
    }
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

    bi_decl(bi_program_description("RPi Pico Drum Machine"));
    bi_decl(bi_1pin_with_name(LED, "On-board LED"));

    sleep_ms(3000);

    // Setup core1
    multicore_launch_core1(interface_core);

    // Initialize Audio
    //...

    // Wait for core1 to finish initialization
    if (!coretalk.handshake()) return 1;

    coretalk.setup();
    coretalk.set_callback(&audio_core_handler);

    absolute_time_t now_timestamp = nil_time;
    while (1) {
        now_timestamp = get_absolute_time();
        sleep_ms(1000);
    }

    return 0;
}
