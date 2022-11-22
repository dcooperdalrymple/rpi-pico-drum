cmake_minimum_required(VERSION 3.13)

set(NAME rpi-pico-drum)
set(DESC "RPi Pico Drum Machine")
set(VERSION "0.2.0")
set(URL "https://github.com/dcooperdalrymple/rpi-pico-drum")

# initialize pico-sdk from GIT
# (note this can come from environment, CMake cache etc)
set(PICO_SDK_FETCH_FROM_GIT on)

# pico_sdk_import.cmake is a single file copied from this SDK
# note: this must happen before project()
include(pico_sdk_import.cmake)

set(PICO_EXTRAS_PATH ../lib/pico-extras)
include(pico_extras_import.cmake)

# rest of your project
project(${NAME} C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PICO_CXX_ENABLE_EXCEPTIONS 1)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

include_directories(./include)
include_directories(./lib/picojson)
add_executable(${NAME}
    src/hw_config.c
    src/storage.cpp
    src/config.cpp
    src/display.cpp
    src/rotary.cpp
    src/coretalk.cpp
    src/audio.cpp
    src/sample.cpp
    src/mixer.cpp
    main.cpp
)
add_subdirectory(./lib/pi-pico-ss-oled/pico-ss-oled)
add_subdirectory(./lib/pico-neotrellis)
add_subdirectory(./lib/no-OS-FatFS/FatFs_SPI)

pico_generate_pio_header(${NAME} ${CMAKE_CURRENT_LIST_DIR}/src/rotary.pio)

target_link_libraries(${NAME}
    pico_stdlib
    hardware_gpio
    hardware_pio
    hardware_uart
    hardware_pwm
    hardware_irq
    pico_double
    pico_multicore
    pico_ss_oled
    pico_neotrellis
    FatFs_SPI
    pico_audio_i2s
    pico_audio_pwm
)

pico_set_program_name(${NAME} ${DESC})
pico_set_program_version(${NAME} ${VERSION})
pico_set_program_url(${NAME} ${URL})

pico_add_extra_outputs(${NAME})
