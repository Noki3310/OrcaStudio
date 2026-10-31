#!/usr/bin/env python3
"""Compile the production ABI validator and check incompatible library rejection."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/slic3r/Utils/SlicerLinuxRuntime/SlicerLinuxRuntimeConfig.cpp").read_text()
start = source.index("std::string expected_component_abi_version()")
end = source.index("bool validate_linux_component_file_against_manifest", start)
code = r'''#include <string>
#include <cstdlib>
#include <cassert>
void set_reason(std::string* p, const std::string& s) { if (p) *p = s; }
''' + source[start:end] + r'''
int main() {
    unsetenv("SLICER_LINUX_RUNTIME_EXPECTED_ABI_VERSION");
    for (auto v : {"02.08.01", "02.08.01.55"})
        assert(abi_version_matches_expected(v, nullptr));
    for (auto v : {"", "02.08.04", "02.08.010", "02.08.01.", "02.08.01.bad"}) {
        std::string reason;
        assert(!abi_version_matches_expected(v, &reason));
        assert(!reason.empty());
    }
    setenv("SLICER_LINUX_RUNTIME_EXPECTED_ABI_VERSION", "02.08.04", 1);
    assert(!abi_version_matches_expected("02.08.04", nullptr));
    assert(!abi_version_matches_expected("02.08.01.55", nullptr));
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / "abi.cpp"
    binary = Path(directory) / "abi"
    cpp.write_text(code)
    subprocess.run(["g++", "-std=c++17", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=10)
print("Runtime ABI acceptance and rejection checks passed")
