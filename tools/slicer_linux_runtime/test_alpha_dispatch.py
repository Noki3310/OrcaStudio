#!/usr/bin/env python3
"""Exercise the production print dispatcher with a simulated runtime export."""
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[2]
network = (ROOT / "src/slic3r/Utils/bambu_networking.hpp").read_text()
start = network.index("struct PrintParams {")
params = network[start:network.index("\n};", start)+3]
agent = (ROOT / "src/slic3r/Utils/BBLPrinterAgent.cpp").read_text()
start = agent.index("template <typename LegacyFn, typename Fn0203, typename CurrentFn, typename... CallbackFns>")
end = agent.index("\n} // namespace", start)
code = r'''#include "src/slic3r/Utils/SlicerLinuxRuntime/RuntimePrintAdapter.hpp"
#include <cassert>
#include <iostream>
#define BOOST_LOG_TRIVIAL(x) std::cerr
using namespace Slic3r;
''' + params + r'''
enum class NetworkAbi { Legacy, V0203, Current, Runtime020801 };
struct BBLNetworkPlugin {
    static BBLNetworkPlugin& instance(){static BBLNetworkPlugin p; return p;}
    void* get_agent(){return this;}
    NetworkAbi network_abi(){return NetworkAbi::Runtime020801;}
    static PrintParams as_legacy(PrintParams& p){return p;}
    static PrintParams as_0203(PrintParams& p){return p;}
};
struct BBLPrinterAgent {static std::string from_orca_payload(std::string p){return p;}};
template<class T,class F> T as_abi(F f){return reinterpret_cast<T>(f);}
''' + agent[start:end] + r'''
static int calls=0;
int runtime_start(void*, SlicerLinuxRuntime::RuntimePrintParams p, void (*callback)(int)) {
    ++calls;
    assert(p.dev_id=="X1C" && p.slicer_uid=="alpha-client");
    assert(p.task_use_ams && p.ams_mapping2=="[1]");
    callback(7);
    return 42;
}
int main(){
    using Fn=int(*)(void*,PrintParams,void(*)(int));
    auto fn=reinterpret_cast<Fn>(&runtime_start);
    PrintParams p{}; p.dev_id="X1C"; p.slicer_uid="alpha-client";
    p.task_use_ams=true; p.ams_mapping2="[1]";
    void (*cb)(int)=[](int n){assert(n==7);};
    assert((dispatch_start<Fn,Fn>(fn,p,cb)==42));
    assert(calls==1);
    p.queue_plate_id="queued";
    assert((dispatch_start<Fn,Fn>(fn,p,cb)==-1));
    assert(calls==1);
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp=Path(directory)/"dispatch.cpp"
    binary=Path(directory)/"dispatch"
    cpp.write_text(code)
    subprocess.run(["g++","-std=c++17","-I",str(ROOT),str(cpp),"-o",str(binary)],check=True)
    subprocess.run([str(binary)],check=True,timeout=10)
print("Alpha dispatcher: runtime layout, callback, result and queue rejection passed")
