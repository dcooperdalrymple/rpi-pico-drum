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

bool Storage::read_json(const char* filename, picojson::value* data) {
    FIL file;
    FRESULT fr = f_open(&file, filename, FA_READ);
    if (FR_OK != fr && FR_EXIST != fr) return false;

    std::string content;
    char buffer[256];
    while (!f_eof(&file) && f_gets(buffer, sizeof buffer, &file)) {
        content += buffer;
    }

    std::string err = picojson::parse(*data, content);
    if (!err.empty()) return false;

    fr = f_close(&file);
    if (FR_OK != fr) return false;

    return true;
}
