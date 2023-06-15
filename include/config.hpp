/**
 * File: config.hpp
 * Title: Device Configuration
 * Version: 0.2.0
 * Since: 0.2.0
 */

#pragma once
#include "picojson.h"
#include "storage.hpp"

#define CONFIG_FILE "/config.json"

class Config {
    private:
        Storage* storage;
        picojson::value* data;

        template <typename T> T get<T>(const std::string& key, const picojson::value::object& obj = NULL);
        template <typename T> T get_index<T>(const std::string& key, uint index, const picojson::value::object& obj = NULL);
        template <typename T> T get_child<T>(const std::string& parent_key, const std::string& child_key, const picojson::value::object& obj = NULL);

    public:
        Config(Storage* storage);
        bool init(void);

        double get_version(void);

        uint8_t get_midi_channel(void);
        bool get_midi_thru(void);

        size_t get_audio_bufferSize(void);
        uint get_audio_rate(void);
        std::string get_audio_output(void);
        double get_audio_volume(void);

        const picojson::value::array& get_patches(void);
        size_t get_patches_count(void);
        const picojson::value& get_patch(uint index);

        std::string get_patch_name(const picojson::value& patch);
        uint8_t get_patch_program(const picojson::value& patch);
        const picojson::value::array& get_patch_samples(const picojson::value& patch);
        size_t get_patch_samples_count(const picojson::value& patch);
        const picojson::value::object& get_patch_sample(const picojson::value& patch, uint8_t index);

        std::string get_sample_file(const picojson::value::object& sample);
        std::string get_sample_name(const picojson::value::object& sample);
        uint8_t get_sample_note(const picojson::value::object& sample);
        uint8_t get_sample_pad(const picojson::value::object& sample);
        std::string get_sample_color(const picojson::value::object& sample);
        double get_sample_level(const picojson::value::object& sample);
        double get_sample_minLevel(const picojson::value::object& sample);
        double get_sample_pan(const picojson::value::object& sample);
        bool get_sample_loop(const picojson::value::object& sample);
        bool get_sample_noteOff(const picojson::value::object& sample);

}
