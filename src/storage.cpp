/**
 * Package: rpi-pico-drum
 * File: storage.hpp
 * Title: SD Card Storage
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include "storage.hpp"

Storage::Storage(sd_card_t *pSD) :
    pSD(pSD) {

}

bool Storage::init(void) {
    FRESULT fr = f_mount(&pSD->fatfs, pSD->pcName, 1);
    return FR_OK == fr;
}
void Storage::uninit(void) {
    f_unmount(pSD->pcName);
}
