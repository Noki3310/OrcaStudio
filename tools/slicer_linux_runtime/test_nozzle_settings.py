#!/usr/bin/env python3
"""Compile the production X1C nozzle command against a fake publisher. No device I/O."""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/slic3r/GUI/DeviceManager.cpp").read_text()
start = source.index("int MachineObject::command_set_printer_nozzle(")
end = source.index("int MachineObject::command_refresh_nozzle(", start)
prelude = r'''
#include <nlohmann/json.hpp>
#include <string>
#include <stdexcept>
#include <limits>
#include <iostream>
using nlohmann::json;
struct MachineObject {
    std::string printer_type = "BL-P001";
    bool connected = true, printing = false, paused = false, calibrating = false;
    int calls = 0, result = 0;
    static int m_sequence_id;
    json sent;
    bool is_connected() { return connected; }
    bool is_in_printing() { return printing; }
    bool is_in_printing_pause() { return paused; }
    bool is_in_calibration() { return calibrating; }
    int publish_json(const json& j) { ++calls; sent = j; return result; }
    int command_set_printer_nozzle(std::string, float);
};
int MachineObject::m_sequence_id = 0;
void require(bool b) { if (!b) throw std::runtime_error("nozzle command regression"); }
'''
cases = r'''
int main() {
    int tests = 0;
    for (auto model : {"BL-P001", "3DPrinter-X1-Carbon"})
        for (auto type : {"hardened_steel", "stainless_steel"})
            for (float diameter : {0.2f, 0.4f, 0.6f, 0.8f}) {
                MachineObject m; m.printer_type = model;
                require(m.command_set_printer_nozzle(type, diameter) == 0);
                require(m.calls == 1);
                const auto& j = m.sent.at("system");
                require(j.at("command") == "set_accessories" && j.at("accessory_type") == "nozzle");
                require(j.at("nozzle_type") == type && j.at("nozzle_diameter").get<float>() == diameter);
                require(j.at("sequence_id").is_string()); ++tests;
            }
    for (int scenario = 0; scenario < 9; ++scenario) {
        MachineObject m; std::string type = "hardened_steel"; float diameter = 0.6f;
        switch (scenario) {
        case 0: m.connected = false; break;
        case 1: m.printing = true; break;
        case 2: m.paused = true; break;
        case 3: m.calibrating = true; break;
        case 4: m.printer_type = "C11"; break;
        case 5: type = "unknown"; break;
        case 6: diameter = 0.5f; break;
        case 7: diameter = std::numeric_limits<float>::quiet_NaN(); break;
        case 8: m.printer_type.clear(); break;
        }
        require(m.command_set_printer_nozzle(type, diameter) == -1 && m.calls == 0); ++tests;
    }
    MachineObject m; m.result = -42;
    require(m.command_set_printer_nozzle("hardened_steel", 0.6f) == -42 && m.calls == 1); ++tests;
    std::cout << tests << " nozzle command cases passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix="nozzle-test-") as tmp:
    cpp = Path(tmp) / "test.cpp"
    exe = Path(tmp) / "test"
    cpp.write_text(prelude + source[start:end] + cases)
    subprocess.run([os.environ.get("CXX", "g++"), "-std=c++17", "-Wall", "-Wextra",
                    "-I", str(ROOT / "deps_src"), str(cpp), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
