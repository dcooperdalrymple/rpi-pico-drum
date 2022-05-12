/**
 * Package: rpi-pico-drum
 * File: rotary.cpp
 * Title: Rotary Encoders with PIO
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include "rotary.hpp"

int Rotary::pin_clk = -1;
int Rotary::pin_dt = -1;
int Rotary::pin_sw = -1;

uint8_t Rotary::sw_state = 0;
rotary_callback_t Rotary::cb = NULL;

int Rotary::rotation = 0;
