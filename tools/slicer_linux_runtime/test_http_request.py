#!/usr/bin/env python3
"""Run the actual HTTP export with a fake RPC peer, without a GUI/WSL build.

The function body is extracted verbatim from the supplied production source.
Only RpcClient and the shutdown flag are substituted. No network is contacted.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/slic3r/Utils/SlicerLinuxRuntime/SlicerLinuxRuntimeForwarderExports.cpp"

PRELUDE = r'''
#include <nlohmann/json.hpp>
#include <atomic>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
using nlohmann::json;
#define SLICER_LINUX_RUNTIME_EXPORT
#define SLIC3R_APP_NAME "OrcaStudio"
#define SLIC3R_VERSION "02.08.01.55"
std::atomic<bool> g_forwarder_shutting_down{false};
struct Reply { json payload; std::vector<unsigned char> binary; };
struct RpcClient {
    Reply start{{{"ok", true}, {"job", 7}}, {}};
    std::vector<Reply> statuses;
    size_t next = 0;
    int releases = 0, cancels = 0, starts = 0;
    static RpcClient& instance() { static RpcClient client; return client; }
    Reply invoke_binary(const std::string& method, const json& args,
                        const std::vector<unsigned char>& body = {}) {
        if (method == "http.start") { ++starts; return start; }
        if (method != "http.status" || args.at("job") != 7 || next >= statuses.size())
            throw std::runtime_error("unexpected RPC request");
        return statuses.at(next++);
    }
    void invoke_void(const std::string& method, const json& args) {
        if (args.at("job") != 7) throw std::runtime_error("wrong job ID");
        if (method == "http.release") ++releases;
        else if (method == "http.cancel") ++cancels;
        else throw std::runtime_error("unexpected RPC command");
    }
};
'''

CASES = r'''
void require(bool ok, const std::string& message) {
    if (!ok) throw std::runtime_error(message);
}
int main(int argc, char** argv) {
    try {
        const std::string name = argv[1];
        auto& rpc = RpcClient::instance();
        unsigned status = 0;
        std::string body, headers, ip, error;
        unsigned long long limit = 8;
        std::string metadata = "[]";
        int expected_rc = -1, expected_releases = 1;
        std::string expected_error;
        int (*progress)(void*, unsigned long long, unsigned long long,
                        unsigned long long, unsigned long long, double) = nullptr;
        bool (*cancel)(void*) = nullptr;
        auto done = json{{"ok", true}, {"done", true}, {"transport_ok", true},
                         {"http_status", 200}, {"response_headers", "X: y"}, {"primary_ip", "127.0.0.1"}};
        if (name == "status_failure") {
            expected_error = "runtime host stopped";
            rpc.statuses = {{{{"ok", false}, {"error", expected_error}}, {}}};
        } else if (name == "status_failure_without_detail") {
            expected_error = "Linux HTTP status failed";
            rpc.statuses = {{{{"ok", false}}, {}}};
        } else if (name == "shutdown") {
            expected_error = "Linux runtime forwarder is shutting down";
            g_forwarder_shutting_down = true;
        } else if (name == "offset_mismatch") {
            expected_error = "Linux HTTP response stream offset mismatch";
            rpc.statuses = {{{{"ok", true}, {"chunk_offset", 3}}, {'x'}}};
        } else if (name == "size_limit") {
            expected_error = "Linux HTTP response exceeds limit";
            limit = 2;
            rpc.statuses = {{{{"ok", true}, {"chunk_offset", 0}}, {'a','b','c'}}};
        } else if (name == "partial_then_failure") {
            expected_error = "unknown HTTP job";
            rpc.statuses = {{{{"ok", true}, {"chunk_offset", 0}}, {'a','b'}},
                            {{{"ok", false}, {"error", expected_error}}, {}}};
        } else if (name == "success_stream") {
            expected_rc = 0;
            done["chunk_offset"] = 2;
            rpc.statuses = {{{{"ok", true}, {"chunk_offset", 0}}, {'a','b'}}, {done, {'c'}}};
        } else if (name == "http_404") {
            expected_rc = 0; // HTTP failure is handled by Http.cpp, transport succeeded.
            done["http_status"] = 404;
            rpc.statuses = {{done, {}}};
        } else if (name == "network_failure") {
            expected_error = "TLS connection failed";
            done["transport_ok"] = false;
            done["http_status"] = 0;
            done["error"] = expected_error;
            rpc.statuses = {{done, {}}};
        } else if (name == "cancel") {
            expected_error = "cancelled";
            cancel = +[](void*) { return true; };
            done["transport_ok"] = false;
            done["http_status"] = 0;
            done["error"] = expected_error;
            rpc.statuses = {{{{"ok", true}}, {}}, {done, {}}};
        } else if (name == "callback_exception") {
            expected_error = "Linux HTTP callback failed: callback error";
            progress = +[](void*, unsigned long long, unsigned long long,
                           unsigned long long, unsigned long long, double) -> int {
                throw std::runtime_error("callback error");
            };
            done["transport_ok"] = false;
            done["http_status"] = 0;
            done["error"] = "cancelled";
            rpc.statuses = {{done, {}}};
        } else if (name == "start_failure") {
            expected_releases = 0;
            expected_error = "host unavailable";
            rpc.start.payload = {{"ok", false}, {"error", expected_error}};
        } else if (name == "invalid_job") {
            expected_releases = 0;
            expected_error = "Linux HTTP request returned an invalid job ID";
            rpc.start.payload["job"] = 0;
        } else if (name == "invalid_metadata") {
            expected_releases = 0;
            metadata = "{";
        } else if (name == "null_outputs") {
            rpc.statuses = {{{{"ok", false}}, {}}};
        } else {
            throw std::runtime_error("unknown test case");
        }
        bool null_outputs = name == "null_outputs";
        const int rc = slicer_linux_runtime_http_request("GET", "https://example.invalid/hms", metadata,
            "", "[]", "", limit, 1000, 1000, progress, cancel, nullptr,
            null_outputs ? nullptr : &status, null_outputs ? nullptr : &body,
            null_outputs ? nullptr : &headers, null_outputs ? nullptr : &ip,
            null_outputs ? nullptr : &error);
        require(rc == expected_rc, "wrong return code");
        require(rpc.releases == expected_releases, "job not released exactly once");
        if (!null_outputs && name != "invalid_metadata") require(error == expected_error, "lost original diagnostic: " + error);
        if (name == "invalid_metadata") {
            require(error.find("invalid Linux HTTP metadata JSON:") == 0, "wrong metadata diagnostic");
            require(rpc.starts == 0, "invalid metadata reached RPC");
        }
        if (name == "success_stream") {
            require(body == "abc", "stream body changed");
            require(status == 200 && headers == "X: y" && ip == "127.0.0.1", "success metadata changed");
        } else if (name == "partial_then_failure") {
            require(body == "ab", "partial body lost");
            require(status == 0 && headers.empty() && ip.empty(), "abort exposed successful metadata");
        } else if (name == "http_404") require(status == 404, "HTTP status lost");
        else require(status == 0, "failed request has HTTP success status");
        require(rpc.cancels == ((name == "cancel" || name == "callback_exception") ? 1 : 0), "incorrect cancellation count");
        std::cout << "PASS " << name << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "FAIL " << argv[1] << ": " << e.what() << '\n';
        return 1;
    }
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    args = parser.parse_args()
    compiler = os.environ.get("CXX", "g++")
    if not shutil.which(compiler):
        raise SystemExit(f"C++17 compiler unavailable: {compiler}")
    source = args.source.read_text(encoding="utf-8")
    start = source.index("SLICER_LINUX_RUNTIME_EXPORT int slicer_linux_runtime_http_request(")
    end = source.index("SLICER_LINUX_RUNTIME_EXPORT int slicer_linux_runtime_http_get(", start)
    with tempfile.TemporaryDirectory(prefix="runtime-http-test-") as temp:
        cpp = Path(temp) / "http_test.cpp"
        binary = Path(temp) / "http_test"
        cpp.write_text(PRELUDE + source[start:end] + CASES, encoding="utf-8")
        subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Wno-unused-parameter", "-pthread",
                        "-I", str(ROOT / "deps_src"), str(cpp), "-o", str(binary)], check=True)
        cases = ["status_failure", "status_failure_without_detail", "shutdown", "offset_mismatch", "size_limit",
                 "partial_then_failure", "success_stream", "http_404", "network_failure", "cancel",
                 "callback_exception", "start_failure", "invalid_job", "invalid_metadata", "null_outputs"]
        failures = 0
        for case in cases:
            result = subprocess.run([str(binary), case], capture_output=True, text=True, timeout=10)
            print((result.stdout + result.stderr).strip())
            failures += result.returncode != 0
        print(f"{len(cases) - failures}/{len(cases)} HTTP behavior tests passed")
        return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
