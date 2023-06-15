/**
 * Package: rpi-pico-drum
 * File: config.cpp
 * Title: Device Configuration
 * Version: 0.2.0
 * Since: 0.2.0
 */

#include "config.hpp"

Config::Config(Storage* storage) :
    storage(storage) {

}

bool Config::valid_data(picojson::value* data_ptr = NULL) {
    if (data_ptr == NULL) data_ptr = data;
    return !data_ptr->is<picojson::null>() && data_ptr->is<picojson::object>();
}

bool Config::init(void) {
    if (!storage->read_json(CONFIG_FILE, data)) return false;
    if (!valid_data()) return false;
    return true;
}

template <typename T> T Config::get<T>(const std::string& key, const picojson::value::object& obj = NULL) {
    if (obj == NULL) {
        if (!valid_data()) return NULL;
        obj = data->get<picojson::object>();
    } else {
        if (!valid_data(obj)) return NULL;
    }

    if (!obj.contains(key)) return NULL;

    const picojson::value& value = obj.get(key);
    if (!value.is<T>()) return NULL;

    return value.get<T>();
}

template <typename T> T Config::get_index<T>(const std::string& key, uint index, const picojson::value::object& obj = NULL) {
    const picojson::value::array& elements = get<picojson::value::array>(key, obj);
    if (patches == NULL) return NULL;

    const picojson::value& element = std::find(elements.begin(), elements.end(), index);
    if (element == elements.end() || !element.is<T>()) return NULL;

    return element.get<T>();
}

template <typename T> T Config::get_child<T>(const std::string& parent_key, const std::string& child_key, const picojson::value::object& obj = NULL) {
    if (obj == NULL) {
        if (!valid_data()) return NULL;
        obj = data->get<picojson::object>();
    }

    if (!obj.contains(key)) return NULL;

    const picojson::value& parent = obj.get(parent_key);
    return get<T>(child_key, parent);
}

double Config::get_version(void) {
    return get<double>("version");
}

uint8_t Config::get_midi_channel(void) {
    return (uint8_t)get_child<double>("midi", "channel");
}
bool Config::get_midi_thru(void) {
    return get_child<bool>("midi", "thru");
}

size_t Config::get_audio_bufferSize(void) {
    return (size_t)get<double>("audio", "bufferSize");
}
uint Config::get_audio_rate(void) {
    return (uint)get<double>("audio", "rate");
}
std::string Config::get_audio_output(void) {
    return get<std::string>("audio", "output");
}
double Config::get_audio_volume(void) {
    return get<double>("audio", "bufferSize");
}

const picojson::value::array& Config::get_patches(void) {
    return get<picojson::value::array>("patches");
}
size_t Config::get_patches_count(void) {
    return get_patches().size();
}
const picojson::value& Config::get_patch(uint index) {
    return get_index<picojson::value>("patches", index);
}

std::string Config::get_patch_name(const picojson::value& patch) {
    return get<std::string>("name", patch);
}
uint8_t Config::get_patch_program(const picojson::value& patch) {
    return (uint8_t)get<double>("program", patch);
}
const picojson::value::array& Config::get_patch_samples(const picojson::value& patch) {
    return get<picojson::value::array>("samples", patch);
}
size_t Config::get_patch_samples_count(const picojson::value& patch) {
    return get_patch_samples(patch).size();
}
const picojson::value::object& Config::get_patch_sample(const picojson::value& patch, uint8_t index) {
    return get_index<picojson::value::object>("samples", index, patch);
}

std::string Config::get_sample_file(const picojson::value::object& sample) {
    return get<std::string>("file", sample);
}
std::string Config::get_sample_name(const picojson::value::object& sample) {
    return get<std::string>("name", sample);
}
uint8_t Config::get_sample_note(const picojson::value::object& sample) {
    return (uint8_t)get<double>("note", sample);
}
uint8_t Config::get_sample_pad(const picojson::value::object& sample) {
    return (uint8_t)get<double>("pad", sample);
}
std::string Config::get_sample_color(const picojson::value::object& sample) {
    return get<std::string>("color", sample);
}
double Config::get_sample_level(const picojson::value::object& sample) {
    return get<double>("level", sample);
}
double Config::get_sample_minLevel(const picojson::value::object& sample) {
    return get<double>("minLevel", sample);
}
double Config::get_sample_pan(const picojson::value::object& sample) {
    return get<double>("pan", sample);
}
bool Config::get_sample_loop(const picojson::value::object& sample) {
    return get<bool>("loop", sample);
}
bool Config::get_sample_noteOff(const picojson::value::object& sample) {
    return get<bool>("noteOff", sample);
}
