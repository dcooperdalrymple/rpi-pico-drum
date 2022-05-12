/**
 * Package: rpi-pico-drum
 * File: display.hpp
 * Title: SSD1306 Display Control
 * Version: 0.2.0
 * Since: 0.2.0
 */

#pragma once
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/double.h"
#include "ss_oled.hpp"
#include "hw_config.h"

#define OLED_WIDTH  128
#define OLED_HEIGHT 64

#define STRLEN      32

class Display {

private:

    int rc;
    picoSSOLED oled;
    uint8_t ucBuffer[1024];
    char textBuffer[STRLEN];

    bool awake = false;
    bool powered = true;

    void copyConstStr(const char *msg) {
        if (strlen(msg) >= STRLEN) return;
        strcpy(textBuffer, msg);
    };

public:

    Display() : oled(OLED_128x64, 0x3c, 0, 0, DISPLAY_I2C, DISPLAY_SDA, DISPLAY_SCL, I2C_SPEED) {
        rc = oled.init();
        oled.set_back_buffer(ucBuffer);
        if (rc == OLED_NOT_FOUND) return;

        oled.fill(0x00, 1);
        wake();
    };

    void dump() {
        if (rc == OLED_NOT_FOUND) return;
        oled.dump_buffer(NULL);
    };

    void clear() {
        if (rc == OLED_NOT_FOUND) return;
        oled.set_back_buffer(ucBuffer);
        oled.fill(0, 1);
    };

    void sleep(void) {
        if (rc == OLED_NOT_FOUND) return;
        oled.set_contrast(0);
        awake = false;
    };
    void wake(void) {
        if (rc == OLED_NOT_FOUND) return;
        if (!powered) power_on();
        oled.set_contrast(127);
        awake = true;
    };
    bool is_awake(void) {
        return awake;
    };

    void power_off(void) {
        if (rc == OLED_NOT_FOUND) return;
        if (powered == false) return;
        oled.power(false);
        powered = false;
    };
    void power_on(void) {
        if (rc == OLED_NOT_FOUND) return;
        if (powered == true) return;
        oled.power(true);
        powered = true;
        oled.fill(0x00, 1);
        dump();
    };
    bool is_powered(void) {
        return powered;
    };

};
