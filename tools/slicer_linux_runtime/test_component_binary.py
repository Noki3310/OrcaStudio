#!/usr/bin/env python3
"""Check the production binary validator used before installing downloaded components."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/slic3r/Utils/SlicerLinuxRuntime/SlicerLinuxRuntimeConfig.cpp").read_text()
helpers = source[source.index("constexpr unsigned char ELF_MAGIC_0"):source.index("std::string env_or")]
start = source.index("bool validate_linux_so_binary(")
validator = source[start:source.index("std::string linux_component_manifest_file_name()", start)]
code = r'''#include <array>
#include <cstdint>
#include <fstream>
#include <string>
#include <utility>
#include <cassert>
''' + helpers + validator + r'''
int main(int argc, char** argv) {
    assert(argc == 2);
    std::string path = std::string(argv[1]) + "/component.so", reason;
    assert(!validate_linux_so_binary(path, &reason));
    std::array<unsigned char, 32> valid{};
    valid[0]=0x7f; valid[1]='E'; valid[2]='L'; valid[3]='F';
    valid[4]=2; valid[5]=1; valid[6]=1; valid[18]=62;
    auto write = [&](const auto& bytes, size_t n) {
        std::ofstream out(path, std::ios::binary | std::ios::trunc);
        out.write(reinterpret_cast<const char*>(bytes.data()), n);
    };
    write(valid, valid.size());
    assert(validate_linux_so_binary(path, &reason));
    for (size_t offset : {size_t(0), size_t(4), size_t(5), size_t(6), size_t(18)}) {
        auto broken = valid; broken[offset]=0;
        write(broken, broken.size());
        assert(!validate_linux_so_binary(path, &reason));
        assert(!reason.empty());
    }
    auto arm = valid; arm[18]=183;
    write(arm, arm.size());
    assert(!validate_linux_so_binary(path, &reason));
    write(valid, 10);
    assert(!validate_linux_so_binary(path, &reason));
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / "component.cpp"
    binary = Path(directory) / "component"
    cpp.write_text(code)
    subprocess.run(["g++", "-std=c++17", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary), directory], check=True, timeout=10)
print("Component validator: x86-64 accepted; missing, truncated and incompatible files rejected")
