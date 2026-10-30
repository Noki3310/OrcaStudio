#!/usr/bin/env python3
"""Exercise the production JSON codec and the separate Linux host decoder."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    if not compiler:
        raise RuntimeError("A C++17 compiler is required")
    host = (ROOT / "tools/slicer_linux_runtime_host/LinuxRuntimeHost.cpp").read_text()
    start = host.index("BBL::PrintParams print_params_from_json(")
    end = host.index("\ntemplate <typename Value>", start)
    source = r'''
#include "shared/slicer_linux_runtime_core/RuntimeCoreJson.hpp"
#include <iostream>
#include <stdexcept>
using namespace Slic3r;
void translate_print_params_paths(BBL::PrintParams&) {}
'''
    source += host[start:end]
    source += r'''
int main() {
    namespace codec = Slic3r::SlicerLinuxRuntime::JsonRuntime;
    BBL::PrintParams input{};
    input.slicer_uid = "alpha-client-identity";
    input.svc_context = "context";
    input.dev_id = "test-device";
    input.ams_mapping2 = "[1,2]";
    input.task_timelapse_use_internal = true;
    input.task_use_ams = true;
    input.extruder_cali_manual_mode = 2;
    const auto wire = codec::to_json(input);
    if (wire.at("slicer_uid") != input.slicer_uid)
        throw std::runtime_error("Client identity was lost during serialization");
    if (codec::to_json(codec::print_params_from_json(wire)) != wire)
        throw std::runtime_error("Shared codec round trip changed print parameters");
    if (codec::to_json(print_params_from_json(wire)) != wire)
        throw std::runtime_error("Linux host decoded different print parameters");
    auto old_wire = wire;
    old_wire.erase("slicer_uid");
    if (!print_params_from_json(old_wire).slicer_uid.empty())
        throw std::runtime_error("Older clients must retain the empty identity default");
    std::cout << "Print parameter identity, round trips and older-client compatibility passed\n";
}
'''
    with tempfile.TemporaryDirectory(prefix="orca-print-params-") as directory:
        cpp = Path(directory) / "test.cpp"
        binary = Path(directory) / "test"
        cpp.write_text(source)
        subprocess.run([compiler, "-std=c++17", "-I", str(ROOT), "-I", str(ROOT / "deps_src"),
                        str(cpp), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True, timeout=10)


if __name__ == "__main__":
    main()
