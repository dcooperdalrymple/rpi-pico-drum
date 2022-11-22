/**
 * Package: rpi-pico-drum
 * File: storage.hpp
 * Title: SD Card Storage
 * Version: 0.2.0
 * Since: 0.2.0
 */

#pragma once

#include "ff.h"
#include "sd_card.h"
#include "hw_config.h"

class Storage {
    private:
        sd_card_t *pSD;

    public:
        Storage(sd_card_t *pSD);
        bool init(void);
        void uninit(void);

};
