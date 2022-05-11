#pragma once
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/pio.h"
#include "hardware/irq.h"

#include "../build/rotary.pio.h"

#define ROTARY_CW      1
#define ROTARY_CCW     2
#define ROTARY_PRESS   3
#define ROTARY_RELEASE 4

typedef void(* rotary_callback_t) (uint8_t event);

class Rotary {

private:

    uint sm; // pio state machine

    PIO pio = NULL;

    static int pin_clk;
    static int pin_dt;
    static int pin_sw;

    static uint8_t sw_state;

    static rotary_callback_t cb;
    static int rotation;

    static void process_rotary() {
        if (!(pio0_hw->irq & 3)) return;
        io_rw_32 *irq = &pio0_hw->irq;

        if (*irq & 1) {
            rotation += 1;
            if (cb) cb(ROTARY_CW);
        } else if (*irq & 2) {
            rotation -= 1;
            if (cb) cb(ROTARY_CCW);
        }

        // Clear interrupts
        *irq = 3;
    };

    static void process_switch(uint gpio, uint32_t events) {
        gpio_acknowledge_irq(gpio, events);
        if (gpio != pin_sw) return;
        if (sw_state == (uint8_t)gpio_get(gpio)) return;

        sw_state = (uint8_t)gpio_get(gpio);
        if (sw_state) {
            if (cb) cb(ROTARY_RELEASE);
        } else {
            if (cb) cb(ROTARY_PRESS);
        }
    };

public:

    Rotary(int clk, int sw) { // dt must be pin next to clk
        sm = 0;

        pin_clk = clk;
        pin_dt = clk+1;
        pin_sw = sw;

        // Configure pins and PIO program
        pio = pio0;

        pio_gpio_init(pio, pin_clk);
        pio_gpio_init(pio, pin_dt);

        uint offset = pio_add_program(pio, &pio_rotary_encoder_program);
        pio_sm_config c = pio_rotary_encoder_program_get_default_config(offset);

        sm_config_set_in_pins(&c, pin_clk);
        sm_config_set_in_shift(&c, false, false, 0); // LSB, no autopush

        // Configure IRQ
        irq_set_exclusive_handler(PIO0_IRQ_0, &process_rotary);
        irq_set_enabled(PIO0_IRQ_0, true);
        pio0_hw->inte0 = PIO_IRQ0_INTE_SM0_BITS | PIO_IRQ0_INTE_SM1_BITS;

        // Setup the State Machine
        pio_sm_init(pio, sm, 16, &c); // 16 = program counter after jump table
        pio_sm_set_enabled(pio, sm, true);

        gpio_init(pin_sw);
        gpio_set_dir(pin_sw, GPIO_IN);
        gpio_set_irq_enabled_with_callback(pin_sw, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &process_switch);
    };

    void set_callback(rotary_callback_t callback) {
        cb = callback;
    };
    void clear_callback(void) {
        cb = NULL;
    };

    void set_rotation(int value) {
        rotation = value;
    };
    int get_rotation(void) {
        return rotation;
    };

};
