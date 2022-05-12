/**
 * Package: rpi-pico-drum
 * File: hw_config.h
 * Title: RP2040 Hardware Assignment
 * Version: 0.2.0
 * Since: 0.2.0
 */

#ifndef HW_CONFIG_H_
#define HW_CONFIG_H_

#define LED             25

// I2C

#define I2C_SPEED       100 * 1000

#define DISPLAY_I2C     i2c0
#define DISPLAY_SDA     20
#define DISPLAY_SCL     21

#define TRELLIS_I2C     i2c1
#define TRELLIS_SDA     18
#define TRELLIS_SCL     19

// Rotary Encoders

#define ROTARY_BOUNCE   4
#define ROTARY_RESET    500

#define MENU_CLK        12
#define MENU_DT         13
#define MENU_SW         7

#define MOD_CLK         26
#define MOD_DT          27
#define MOD_SW          28

// UART/MIDI

#define MIDI_UART       uart1
#define MIDI_TX         4
#define MIDI_RX         5

// SD Card

#define SD_DO           8
#define SD_CS           9
#define SD_CLK          10
#define SD_DI           11

// Audio

#define PWM_L           16
#define PWM_R           17

#define I2S_CLK         0
#define I2S_SEL         1
#define I2S_DATA        2

#endif
