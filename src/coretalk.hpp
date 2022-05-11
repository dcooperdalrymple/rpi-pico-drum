#pragma once
#include "pico/multicore.h"
#include "hardware/irq.h"

#define CORE_HANDSHAKE  123
#define CORE_POKE       69
#define CORE_DATA       87
#define CORE_NUM        2

typedef void(* core_talk_callback_t) (uint32_t event, uint32_t value);

class CoreTalk {
private:

    static core_talk_callback_t cb[CORE_NUM];

    uint8_t i;

    bool buffer_wready(bool block = true) {
        while (!multicore_fifo_wready()) {
            if (!block) return false;
            tight_loop_contents();
        }
        return true;
    };
    bool buffer_rvalid(bool block = true) {
        while (!multicore_fifo_rvalid()) {
            if (!block) return false;
            tight_loop_contents();
        }
        return true;
    };

    static void handler() {
        while (multicore_fifo_rvalid()) {
            switch (multicore_fifo_pop_blocking()) {
                case CORE_POKE:
                    if (cb[sio_hw->cpuid]) cb[sio_hw->cpuid](CORE_POKE, 0);
                    break;
                case CORE_DATA:
                    while (!multicore_fifo_rvalid()) tight_loop_contents();
                    if (cb[sio_hw->cpuid]) cb[sio_hw->cpuid](CORE_DATA, multicore_fifo_pop_blocking());
                    break;
            }
        }
        multicore_fifo_clear_irq();
    };

public:

    CoreTalk() { };

    void setup() {
        multicore_fifo_clear_irq();
        if (sio_hw->cpuid) {
            irq_set_exclusive_handler(SIO_IRQ_PROC1, handler);
            irq_set_enabled(SIO_IRQ_PROC1, true);
        } else {
            irq_set_exclusive_handler(SIO_IRQ_PROC0, handler);
            irq_set_enabled(SIO_IRQ_PROC0, true);
        }
    };

    bool handshake() {
        if (sio_hw->cpuid) multicore_fifo_push_blocking(CORE_HANDSHAKE);
        if (multicore_fifo_pop_blocking() != CORE_HANDSHAKE) return false;
        if (!sio_hw->cpuid) multicore_fifo_push_blocking(CORE_HANDSHAKE);
        return true;
    };

    bool poke(bool block = true) {
        if (!buffer_wready(block)) return false;
        multicore_fifo_push_blocking(CORE_POKE);
        return true;
    };

    bool data(uint32_t value, bool block = true) {
        if (!buffer_wready(block)) return false;
        multicore_fifo_push_blocking(CORE_DATA);
        buffer_wready(true);
        multicore_fifo_push_blocking(value);
        return true;
    };

    void set_callback(core_talk_callback_t callback) {
        cb[sio_hw->cpuid] = callback;
    };
    void clear_callback(void) {
        cb[sio_hw->cpuid] = NULL;
    };

};
