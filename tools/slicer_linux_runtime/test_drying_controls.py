#!/usr/bin/env python3
"""Exercise production dry capability/commands with fake devices; never send to hardware."""
from pathlib import Path
import os
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / 'src/slic3r/GUI/DeviceCore/DevFilaSystem.cpp').read_text()
a = src.index('bool DevAms::IsSupportRemoteDry(')
b = src.index('bool DevAms::AmsIsDrying()', a)
capability = src[a:b]
src = (ROOT / 'src/slic3r/GUI/DeviceCore/DevFilaSystemCtrl.cpp').read_text()
a = src.index('int DevFilaSystem::CtrlAmsStartDryingHour(')
commands = src[a:src.rfind('}')]
prelude = r'''
#include <nlohmann/json.hpp>
#include <string>
#include <map>
#include <optional>
#include <vector>
#include <stdexcept>
#include <iostream>
#include <cmath>
#include <limits>
using nlohmann::json;
enum class DevAmsType { AMS, N3F, N3S };
struct MachineObject {
    std::string printer_type = "BL-P001";
    struct Version { std::string name, sw_ver; };
    std::map<std::string, Version> module_vers{{"ota", {"ota", "01.09.01.00"}}};
    bool is_support_remote_dry = false, connected = true, printing = false, paused = false, calibrating = false;
    int calls = 0, result = 0;
    static int m_sequence_id;
    json sent;
    bool is_connected() { return connected; }
    bool is_in_printing() { return printing; }
    bool is_in_printing_pause() { return paused; }
    bool is_in_calibration() { return calibrating; }
    int publish_json(const json& j) { ++calls; sent = j; return result; }
};
int MachineObject::m_sequence_id = 0;
struct DevFilamentDryingPreset {
    std::map<DevAmsType, float> filament_dev_ams_drying_temperature_on_print{{DevAmsType::N3S, 80}};
    float filament_dev_drying_softening_temperature = 90;
    float filament_dev_ams_drying_heat_distortion_temperature = 85;
};
struct Tray {
    bool is_exists = true, ready = true;
    std::optional<DevFilamentDryingPreset> preset{DevFilamentDryingPreset{}};
    bool is_tray_info_ready() const { return ready; }
    auto get_ams_drying_preset() const { return preset; }
};
struct DevAms {
    enum class DryCtrlMode { Off = 0, OnTime = 1 };
    enum class DryStatus { Off, Checking, Drying, Cooling };
    Tray tray;
    std::map<std::string, Tray*> GetTrays() const { return {{"0", const_cast<Tray*>(&tray)}}; }
    DevAmsType type = DevAmsType::N3S;
    std::optional<DryStatus> status{DryStatus::Off};
    std::optional<std::vector<int>> reasons{std::vector<int>{}};
    DevAmsType GetAmsType() const { return type; }
    bool SupportDrying() const { return type == DevAmsType::N3F || type == DevAmsType::N3S; }
    auto GetDryStatus() const { return status; }
    auto GetCannotDryReason() const { return reasons; }
    bool IsSupportRemoteDry(const MachineObject*) const;
};
struct DevFilaSystem {
    MachineObject* m_owner;
    DevAms* ams;
    DevAms* GetAmsById(const std::string& id) const { return id == "128" ? ams : nullptr; }
    bool IsPrintDryTemperatureAllowed(int, int) const;
    int CtrlAmsStartDryingHour(int, std::string, int, int, bool, int, bool = false) const;
    int CtrlAmsStopDrying(int) const;
};
void require(bool b) { if (!b) throw std::runtime_error("drying regression"); }
'''
cases = r'''
int main() {
    int tests = 0;
    for (auto model : {"BL-P001", "3DPrinter-X1-Carbon"}) {
        MachineObject m; m.printer_type = model; DevAms a; DevFilaSystem f{&m, &a};
        require(a.IsSupportRemoteDry(&m));
        require(f.CtrlAmsStartDryingHour(128, "PA-CF", 80, 8, false, 40) == 0);
        require(m.calls == 1);
        const auto& j = m.sent.at("print");
        require(j.at("command") == "ams_filament_drying" && j.at("ams_id") == 128);
        require(j.at("mode") == 1 && j.at("temp") == 80 && j.at("duration") == 8);
        require(j.at("filament") == "PA-CF" && j.at("rotate_tray") == false && j.at("close_power_conflict") == false);
        require(j.at("cooling_temp") == 40 && j.at("humidity") == 0 && j.at("sequence_id").is_string()); ++tests;
        m.printing = true; require(f.CtrlAmsStopDrying(128) == 0);
        require(m.sent.at("print").at("mode") == 0 && m.sent.at("print").at("temp") == 0); ++tests;
    }
    for (int scenario = 0; scenario < 20; ++scenario) {
        MachineObject m; DevAms a; DevFilaSystem f{&m, &a};
        int id = 128, temp = 80, hours = 8; bool rotate = false, override_power = false;
        switch (scenario) {
        case 0: m.connected = false; break;
        case 1: m.printing = true; a.tray.preset.reset(); break;
        case 2: m.paused = true; a.tray.preset.reset(); break;
        case 3: m.calibrating = true; break;
        case 4: m.module_vers.clear(); break;
        case 5: m.module_vers["ota"].sw_ver = "01.08.02.00"; break;
        case 6: m.printer_type = "C11"; break;
        case 7: a.type = DevAmsType::AMS; break;
        case 8: a.type = DevAmsType::N3F; break;
        case 9: temp = 86; break;
        case 10: temp = 44; break;
        case 11: hours = 0; break;
        case 12: hours = 25; break;
        case 13: id = 0; break;
        case 14: a.status.reset(); break;
        case 15: a.status = DevAms::DryStatus::Drying; break;
        case 16: a.reasons = std::vector<int>{1}; break;
        case 17: rotate = true; break;
        case 18: override_power = true; break;
        case 19: f.m_owner = nullptr; break;
        }
        require(f.CtrlAmsStartDryingHour(id, "PA-CF", temp, hours, rotate, 40, override_power) == -1);
        require(m.calls == 0); ++tests;
    }
    MachineObject m; DevAms a; DevFilaSystem f{&m, &a};
    m.result = -42;
    require(f.CtrlAmsStartDryingHour(128, "PA-CF", 80, 8, false, 40) == -42); ++tests;
    require(f.CtrlAmsStopDrying(128) == -42); ++tests;
    require(f.CtrlAmsStopDrying(0) == -1); ++tests;
    m.connected = false; require(f.CtrlAmsStopDrying(128) == -1); ++tests;
    m.connected = true; m.result = 0; m.printer_type = "O1D"; m.is_support_remote_dry = true;
    a.type = DevAmsType::N3F;
    require(a.IsSupportRemoteDry(&m));
    require(f.CtrlAmsStartDryingHour(128, "PETG", 65, 12, true, 40) == 0); ++tests;
    require(f.CtrlAmsStartDryingHour(128, "PETG", 66, 12, false, 40) == -1); ++tests;
    for (bool paused : {false, true}) {
        MachineObject printer; printer.printing = !paused; printer.paused = paused;
        DevAms ht; DevFilaSystem system{&printer, &ht};
        require(system.CtrlAmsStartDryingHour(128, "PA-CF", 80, 8, false, 40) == 0);
        require(printer.sent.at("print").at("rotate_tray") == false); ++tests;
        require(system.CtrlAmsStopDrying(128) == 0); ++tests;
    }
    for (int scenario = 0; scenario < 11; ++scenario) {
        MachineObject printer; printer.printing = true;
        DevAms ht; DevFilaSystem system{&printer, &ht};
        int temp = 80;
        switch (scenario) {
        case 0: ht.tray.is_exists = false; break;
        case 1: ht.tray.ready = false; break;
        case 2: ht.tray.preset.reset(); break;
        case 3: ht.tray.preset->filament_dev_ams_drying_temperature_on_print.clear(); break;
        case 4: ht.tray.preset->filament_dev_ams_drying_temperature_on_print[DevAmsType::N3S] = 0; break;
        case 5: temp = 81; break;
        case 6: ht.tray.preset->filament_dev_drying_softening_temperature = 75; break;
        case 7: ht.tray.preset->filament_dev_ams_drying_heat_distortion_temperature = 75; break;
        case 8: ht.tray.preset->filament_dev_drying_softening_temperature = std::numeric_limits<float>::quiet_NaN(); break;
        case 9: ht.reasons = std::vector<int>{1}; break;
        case 10: printer.calibrating = true; break;
        }
        require(system.CtrlAmsStartDryingHour(128, "PA-CF", temp, 8, false, 40) == -1);
        require(printer.calls == 0); ++tests;
    }
    std::cout << tests << " drying control cases passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix='drying-test-') as tmp:
    cpp = Path(tmp) / 'test.cpp'
    exe = Path(tmp) / 'test'
    cpp.write_text(prelude + capability + commands + cases)
    subprocess.run([os.environ.get('CXX', 'g++'), '-std=c++17', '-Wall', '-Wextra', '-I',
                    str(ROOT / 'deps_src'), str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
