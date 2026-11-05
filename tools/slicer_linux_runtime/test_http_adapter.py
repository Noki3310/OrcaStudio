#!/usr/bin/env python3
"""Exercise the production GUI HTTP adapter with a fake runtime export.

Only filesystem/transport plumbing is substituted, no network or printer is used.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src/slic3r/Utils/Http.cpp').read_text()
header = (ROOT / 'src/slic3r/Utils/Http.hpp').read_text()
plugin = (ROOT / 'src/slic3r/Utils/BBLNetworkPlugin.hpp').read_text()
method = source[source.index('void Http::priv::http_perform_linux_runtime()'):source.index('void Http::priv::http_perform()')]
parts = source[source.index('struct RuntimeMultipartPart'):source.index('struct Http::priv')]
parts = parts.replace('boost::filesystem::ifstream::off_type', 'std::streamoff')
progress = header[header.index('\tstruct Progress'):header.index('\n\ttypedef std::shared_ptr<Http>')]
callbacks = header[header.index('\ttypedef std::function<void(std::string /* body */'):header.index('\n\tHttp(Http &&other)')]
types = plugin[plugin.index('typedef int (*func_linux_http_progress)'):plugin.index('class BBLNetworkPlugin')]
decl = plugin[plugin.index('    static int linux_runtime_http_request('):plugin.index('    // Singleton access')]
prelude = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <climits>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <functional>
#include <limits>
#include <memory>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
namespace fs { using path = std::filesystem::path; using ifstream = std::ifstream; }
struct curl_slist { char* data; curl_slist* next; };
struct form_file { std::ifstream ifs; form_file(const fs::path& p):ifs(p, std::ios::binary) {} };
'''
fake = r'''
static int calls = 0, result = 0;
static unsigned status = 200;
static std::string sent_body, sent_parts;
static long sent_connect, sent_timeout;
int BBLNetworkPlugin::linux_runtime_http_request(
 const std::string&, const std::string&, const std::vector<std::string>&,
 const std::string& body, const std::string& parts, const std::string&,
 std::size_t, long connect, long timeout, func_linux_http_progress progress,
 func_linux_http_cancel cancel, void* user, unsigned* out_status,
 std::string* response, std::string* headers, std::string* ip, std::string* error)
{
 ++calls; sent_body=body; sent_parts=parts; sent_connect=connect; sent_timeout=timeout;
 *out_status=status; *response="reply"; *headers="header"; *ip="127.0.0.1";
 if (result) *error="transport failed";
 progress(user, 5, 5, body.size(), body.size(), 1.0);
 return cancel(user) ? -1 : result;
}
'''
priv = r'''
struct Http::priv {
 static constexpr std::size_t DEFAULT_SIZE_LIMIT = 1024*1024;
 std::atomic<bool> cancel{false};
 std::string buffer, postfields, headers, method="POST", url="https://api.bambulab.com/test", range;
 std::vector<RuntimeMultipartPart> runtime_multipart_parts;
 void* form=nullptr; void* mime=nullptr; curl_slist* headerlist=nullptr;
 std::unique_ptr<form_file> putFile;
 std::size_t limit=0;
 long timeout_connect_seconds=30, timeout_max_seconds=60;
 CompleteFn completefn; ErrorFn errorfn; ProgressFn progressfn;
 IPResolveFn ipresolvefn; HeaderCallbackFn headerfn;
 void http_perform_linux_runtime();
};
'''
tests = r'''
int main() {
 assert(host_matches_domain("API.BAMBULAB.COM.", "bambulab.com"));
 assert(host_matches_domain("bambulab.com", "bambulab.com"));
 assert(!host_matches_domain("evilbambulab.com", "bambulab.com"));
 assert(!host_matches_domain("bambulab.com.evil.test", "bambulab.com"));
 assert(!host_matches_domain("", "bambulab.com"));
 int completed=0, errors=0, received_headers=0, received_ip=0;
 auto prepare = [&](Http::priv& p) {
   p.completefn=[&](std::string body,unsigned code){assert(body=="reply" && code==200);++completed;};
   p.errorfn=[&](std::string,std::string,unsigned){++errors;};
   p.headerfn=[&](std::string h){assert(h=="header");++received_headers;};
   p.ipresolvefn=[&](std::string ip){assert(ip=="127.0.0.1");++received_ip;};
 };
 Http::priv normal;prepare(normal);normal.postfields=std::string("a\0b",3);
 normal.timeout_connect_seconds=LONG_MAX;normal.timeout_max_seconds=LONG_MAX;
 normal.http_perform_linux_runtime();
 assert(calls==1 && completed==1 && errors==0 && sent_body==normal.postfields);
 assert(sent_connect==1800000 && sent_timeout==1800000 && received_headers==1 && received_ip==1);
 for(unsigned code : {0U, 302U, 404U, 500U}) {
   status=code; Http::priv p;prepare(p);p.http_perform_linux_runtime();
 }
 assert(errors==4 && completed==1); status=200;
 result=-1;Http::priv failed;prepare(failed);failed.http_perform_linux_runtime();result=0;
 assert(errors==5 && completed==1);
 Http::priv cancelled;prepare(cancelled);cancelled.cancel=true;int before=calls;
 cancelled.http_perform_linux_runtime();assert(calls==before);
 Http::priv mid;prepare(mid);mid.progressfn=[](Http::Progress,bool& cancel){cancel=true;};
 mid.http_perform_linux_runtime();assert(completed==1 && errors==5);
 std::ofstream("upload.bin",std::ios::binary).write("abcdef",6);
 Http::priv multipart;prepare(multipart);
 multipart.runtime_multipart_parts.push_back({"note",{}, {}, "hello",{},0,0,false});
 multipart.runtime_multipart_parts.push_back({"file","x.bin","application/octet-stream",{},"upload.bin",2,3,true});
 multipart.http_perform_linux_runtime();assert(sent_body=="hellocde");
 auto metadata=nlohmann::json::parse(sent_parts);assert(metadata[1]["offset"]==5 && metadata[1]["size"]==3);
 assert(completed==2);
 for(auto range : std::vector<std::pair<int,int>>{{-1,2},{7,1},{5,2}}) {
   Http::priv p;prepare(p);p.runtime_multipart_parts.push_back({"file",{}, {}, {},"upload.bin",range.first,static_cast<size_t>(range.second),true});
   before=calls;p.http_perform_linux_runtime();assert(calls==before);
 }
 assert(errors==8);
 Http::priv missing;prepare(missing);missing.form=reinterpret_cast<void*>(1);
 missing.http_perform_linux_runtime();assert(errors==9);
 Http::priv put;prepare(put);put.putFile=std::make_unique<form_file>("upload.bin");
 put.http_perform_linux_runtime();assert(sent_body=="abcdef" && !put.putFile && completed==3);
 Http::priv absent;prepare(absent);absent.putFile=std::make_unique<form_file>("absent.bin");
 before=calls;absent.http_perform_linux_runtime();assert(calls==before && errors==10 && !absent.putFile);
 // Sparse file verifies rejection before allocating a gigabyte.
 std::filesystem::resize_file("upload.bin",1024ULL*1024*1024+1);
 Http::priv oversized;prepare(oversized);oversized.putFile=std::make_unique<form_file>("upload.bin");
 before=calls;oversized.http_perform_linux_runtime();assert(calls==before && errors==11);
}
'''
code = prelude + types + '\nclass BBLNetworkPlugin {public:\n' + decl + '\n};\n' + fake
domains = source[source.index('bool host_matches_domain'):source.index('bool is_bambu_linux_runtime_url')]
code += domains
code += '\nclass Http { public: struct priv;\n' + progress + callbacks + '\n};\n' + parts + priv + method + tests
with tempfile.TemporaryDirectory() as directory:
    file=Path(directory)/'adapter.cpp';file.write_text(code)
    exe=Path(directory)/'adapter'
    subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-I',str(ROOT/'deps_src'),str(file),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],cwd=directory,check=True,timeout=20)
print('HTTP adapter: upload ranges, binary bodies, size bounds, timeout overflow, callbacks and cancellation passed')
