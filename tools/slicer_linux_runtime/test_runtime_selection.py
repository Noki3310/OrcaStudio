#!/usr/bin/env python3
"""Check runtime selection defaults, saved preference and environment override."""
from pathlib import Path
import os
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[2]
CODE = r'''
#include "src/slic3r/Utils/RuntimeNetworkSetup.hpp"
#include <cassert>
int main() {
    using namespace Slic3r;
    assert(!runtime_network_requested());
    set_runtime_network_preference(true);
#ifdef _WIN32
    assert(runtime_network_requested());
    setenv("ORCASTUDIO_USE_LINUX_RUNTIME", "0", 1);
    assert(!runtime_network_requested());
    set_runtime_network_preference(false);
    setenv("ORCASTUDIO_USE_LINUX_RUNTIME", "1", 1);
    assert(runtime_network_requested());
    setenv("ORCASTUDIO_USE_LINUX_RUNTIME", "invalid", 1);
    assert(!runtime_network_requested());
    unsetenv("ORCASTUDIO_USE_LINUX_RUNTIME");
    assert(!runtime_network_requested());
#else
    assert(!runtime_network_requested());
    setenv("ORCASTUDIO_USE_LINUX_RUNTIME", "1", 1);
    assert(!runtime_network_requested());
#endif
}
'''
with tempfile.TemporaryDirectory() as directory:
    source=Path(directory)/'selection.cpp';source.write_text(CODE)
    env=os.environ.copy();env.pop('ORCASTUDIO_USE_LINUX_RUNTIME',None)
    for defines in ([], ['-D_WIN32']):
        binary=Path(directory)/'selection'
        subprocess.run(['g++','-std=c++17',*defines,'-I',str(ROOT),str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],env=env,check=True,timeout=10)
print('Runtime selection: native default, saved preference, override and platform gating passed')
