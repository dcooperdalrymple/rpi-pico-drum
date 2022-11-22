/**
 * Package: rpi-pico-drum
 * File: hw_config.cpp
 * Title: SD Card Hardware Definitions
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include <string.h>
#include "hw_config.h"
#include "hw_config.hpp"
#include "ff.h"
#include "diskio.h"
#include "sd_card.h"

void spi0_dma_isr();

static spi_t spis[] = {
    {
        .hw_inst = spi0,
        .miso_gpio = SD_DO,
        .mosi_gpio = SD_DI,
        .sck_gpio = SD_CLK,
        .baud_rate = 12500 * 1000,
        .dma_isr = spi0_dma_isr
    }
};

static sd_card_t sd_cards[] = {
    {
        .pcName = "0:",
        .spi = &spis[0],
        .ss_gpio = SD_CS,
        .use_card_detect = false,
        .card_detect_gpio = -1,
        .card_detected_true = -1,
        .m_Status = STA_NOINIT
    }
};

void spi0_dma_isr() {
    spi_irq_handler(&spis[0]);
}

size_t sd_get_num() {
    return count_of(sd_cards);
}
sd_card_t *sd_get_by_num(size_t num) {
    if (num <= sd_get_num()) {
        return &sd_cards[num];
    } else {
        return NULL;
    }
}
size_t spi_get_num() {
    return count_of(spis);
}
spi_t *spi_get_by_num(size_t num) {
    if (num <= sd_get_num()) {
        return &spis[num];
    } else {
        return NULL;
    }
}
