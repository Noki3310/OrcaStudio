#!/usr/bin/env python3
"""Compile actual source-module/unload methods with fake platform loaders."""
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[2]
s = (ROOT/'src/slic3r/Utils/BBLNetworkPlugin.cpp').read_text()
unload = s[s.index('int BBLNetworkPlugin::unload()'):s.index('bool BBLNetworkPlugin::is_loaded()')]
a=s.index('void* BBLNetworkPlugin::get_source_module()')
a=s.index('{',a)
b=s.index('\nvoid* BBLNetworkPlugin::get_function',a)
source='void* BBLNetworkPlugin::get_source_module()\n'+s[a:b]
code=r'''
#include <cassert>
#include <filesystem>
#include <mutex>
#include <string>
#include <vector>
namespace boost { namespace filesystem = std::filesystem; }
enum class NetworkAbi { Unsupported, Native, Runtime020801 };
static int loads=0, closes=0, destroyed=0, ft_unloads=0, stopped=0;
static int tunnels=0, callbacks=0;
static bool missing=false, enqueue_on_destroy=false;
static std::vector<int> events;
static void* dlopen(const char*,int){++loads;return reinterpret_cast<void*>(2);}
static int dlclose(void*){++closes;events.push_back(3);return 0;}
constexpr int RTLD_LAZY=1;
#define BAMBU_SOURCE_LIBRARY "BambuSource"
std::string data_dir(){return "test-data";}
void UnloadFTModule(){++ft_unloads;events.push_back(2);}
int tunnel_count(){return tunnels;}
int callback_count(){return callbacks;}
void stop(){++stopped;events.push_back(1);}
class BBLNetworkPlugin {
public:
 std::recursive_mutex mutex;
 void* m_networking_module=nullptr;
 void* m_source_module=nullptr;
 NetworkAbi m_network_abi=NetworkAbi::Unsupported;
 auto lock_auth_module(){return std::unique_lock<std::recursive_mutex>(mutex);}
 void destroy_agent(){++destroyed;if(enqueue_on_destroy)callbacks=1;}
 void clear_all_function_pointers(){}
 void* get_function(const char* name){
   if(missing)return nullptr;
   if(std::string(name)=="slicer_linux_runtime_forwarder_active_tunnels")return reinterpret_cast<void*>(&tunnel_count);
   if(std::string(name)=="slicer_linux_runtime_forwarder_active_callbacks")return reinterpret_cast<void*>(&callback_count);
   return reinterpret_cast<void*>(&stop);
 }
 void* get_source_module();
 int unload();
};
'''+source+unload+r'''
int main(){
 BBLNetworkPlugin p;
 assert(p.get_source_module()==nullptr && loads==0);
 p.m_networking_module=reinterpret_cast<void*>(1);p.m_network_abi=NetworkAbi::Runtime020801;
 assert(p.get_source_module()==p.m_networking_module && p.m_source_module==nullptr && loads==0);
 assert(p.get_source_module()==p.m_networking_module && loads==0);
 tunnels=1;assert(p.unload()==-3 && closes==0 && destroyed==0);
 tunnels=0;callbacks=1;assert(p.unload()==-3 && closes==0 && destroyed==0);
 callbacks=0;missing=true;assert(p.unload()==-3 && closes==0 && destroyed==0);
 missing=false;enqueue_on_destroy=true;assert(p.unload()==-3 && closes==0 && destroyed==1 && stopped==0);
 enqueue_on_destroy=false;callbacks=0;assert(p.unload()==0);
 assert(closes==1 && stopped==1 && ft_unloads==1 && p.m_networking_module==nullptr);
 assert(p.m_network_abi==NetworkAbi::Unsupported && (events==std::vector<int>{1,2,3}));
 BBLNetworkPlugin native;native.m_networking_module=reinterpret_cast<void*>(1);native.m_network_abi=NetworkAbi::Native;
 assert(native.get_source_module()==reinterpret_cast<void*>(2) && loads==1);
 assert(native.get_source_module()==reinterpret_cast<void*>(2) && loads==1);
 assert(native.unload()==0 && closes==3 && stopped==1);
}
'''
with tempfile.TemporaryDirectory() as d:
 source=Path(d)/'source.cpp';source.write_text(code);binary=Path(d)/'source'
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra',str(source),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True,timeout=10)
print('Source module: shared runtime handle, no double-close, active stream/callback guards, shutdown order and native fallback passed')
