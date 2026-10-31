#!/usr/bin/env python3
"""Check selection against malformed manifests and mixed network ABI versions."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CODE = r'''
#include "src/slic3r/Utils/NetworkPluginManifest.hpp"
#include <cassert>
using namespace Slic3r;
int main() {
    for (const auto* body : {"not json", "[]", "null", R"({"message":"success","resources":42})"})
        assert(!select_network_plugin_resource(body, "02.08.01.00"));
    auto body = R"({"message":"success","resources":[
        {"version":"02.08.01.9","url":"https://example.org/older"},
        {"version":"02.08.01.55","url":"https://example.org/selected"},
        {"version":"02.08.04.99","url":"https://example.org/wrong-abi"},
        {"version":"02.08.01.999999999999999999999","url":"https://example.org/overflow"},
        {"version":5,"url":"https://example.org/malformed"},
        {"version":"02.08.01.80","url":"http://example.org/insecure"},
        {"version":"02.08.01.90-beta","url":"https://example.org/suffix"},
        {"version":"02.08.01.1","url":"https://example.org/last"}
    ]})";
    auto result = select_network_plugin_resource(body, "02.08.01.00");
    assert(result && result->version == "02.08.01.55");
    assert(result->url == "https://example.org/selected");
    assert(!select_network_plugin_resource(body, "02.09.01.00"));
    assert(!select_network_plugin_resource(body, "02.08.01"));
    assert(!select_network_plugin_resource(R"({"message":"failed","resources":[]})", "02.08.01.00"));
}
'''
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "manifest.cpp"
    binary = Path(directory) / "manifest"
    source.write_text(CODE)
    subprocess.run(["g++", "-std=c++17", "-I", str(ROOT), "-I", str(ROOT / "deps_src"),
                    str(source), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=10)
print("Network manifest: ABI selection, version ordering and malformed responses passed")
