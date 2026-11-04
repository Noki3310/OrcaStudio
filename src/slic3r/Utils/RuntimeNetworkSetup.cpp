#include "RuntimeNetworkSetup.hpp"
#include "SlicerLinuxRuntime/SlicerLinuxRuntimeConfig.hpp"
#include "libslic3r/Utils.hpp"
#include "libslic3r/miniz_extension.hpp"

#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>
#include <boost/process.hpp>
#include <boost/process/windows.hpp>
#include <iterator>
#include <set>
#include <stdexcept>
#include <vector>

namespace Slic3r {
namespace fs = boost::filesystem;
namespace bp = boost::process;

bool install_runtime_network_package(const std::string& archive_path,
                                     const std::string& bundle_dir,
                                     const std::function<bool()>& canceled,
                                     std::string& error)
{
    const fs::path parent = fs::path(data_dir()) / "plugins";
    const fs::path target = parent / "linux-runtime";
    const fs::path staging = parent / fs::unique_path("runtime-stage-%%%%-%%%%-%%%%");
    const fs::path previous = parent / fs::unique_path("runtime-previous-%%%%-%%%%-%%%%");
    mz_zip_archive archive{};
    bool archive_open = false;
    bool moved_previous = false;
    auto check_cancel = [&] {
        if (canceled && canceled()) throw std::runtime_error("Runtime installation canceled");
    };
    try {
        check_cancel();
        fs::create_directories(staging);
        if (!open_zip_reader(&archive, archive_path))
            throw std::runtime_error("Cannot open Linux network package");
        archive_open = true;
        const std::set<std::string> allowed = {
            "libbambu_networking.so", "libBambuSource.so", "liblive555.so",
            "libagora_rtc_sdk.so", "libagora-fdkaac.so", "linux_component_manifest.json"
        };
        std::set<std::string> extracted;
        mz_uint64 total = 0;
        constexpr mz_uint64 limit = 512ULL * 1024ULL * 1024ULL;
        for (mz_uint i = 0; i < mz_zip_reader_get_num_files(&archive); ++i) {
            check_cancel();
            mz_zip_archive_file_stat stat{};
            if (!mz_zip_reader_file_stat(&archive, i, &stat))
                throw std::runtime_error("Cannot read network package entry");
            if (stat.m_is_directory) continue;
            const fs::path relative(decode_archive_entry_path(&archive, stat));
            if (relative.is_absolute() || relative.has_root_name())
                throw std::runtime_error("Absolute path in network package");
            for (const auto& part : relative)
                if (part == "..") throw std::runtime_error("Parent path in network package");
            const auto name = relative.filename().string();
            if (!allowed.count(name)) continue;
            if (!extracted.insert(name).second)
                throw std::runtime_error("Duplicate network package component: " + name);
            if (stat.m_uncomp_size == 0 || stat.m_uncomp_size > limit || total > limit - stat.m_uncomp_size)
                throw std::runtime_error("Invalid network package size");
            total += stat.m_uncomp_size;
            if (!extract_zip_entry_to_file(&archive, i, staging / name))
                throw std::runtime_error("Cannot extract network package component: " + name);
        }
        close_zip_reader(&archive);
        archive_open = false;
        for (const auto* required : {"libbambu_networking.so", "libBambuSource.so"})
            if (!extracted.count(required))
                throw std::runtime_error(std::string("Missing network component: ") + required);
        for (const auto& name : extracted) {
            if (name == "linux_component_manifest.json") continue;
            std::string reason;
            if (!SlicerLinuxRuntime::validate_linux_component_file((staging / name).string(), &reason))
                throw std::runtime_error(name + ": " + reason);
        }
        if (extracted.count("linux_component_manifest.json")) {
            std::string reason;
            if (!SlicerLinuxRuntime::validate_linux_component_set_against_manifest(staging, &reason))
                throw std::runtime_error(reason);
        }
        const auto script = fs::path(bundle_dir) / "install_runtime.ps1";
        const auto powershell = bp::search_path("powershell.exe");
        if (!fs::is_regular_file(script) || powershell.empty())
            throw std::runtime_error("Bundled runtime installer or PowerShell is missing");
        const fs::path cache = fs::path(data_dir()) / "ota" / "plugins";
        fs::create_directories(cache);
        const std::string distro = "OrcaStudio-Alpha-Runtime";
        const fs::path output = staging / "setup.log";
        const fs::path errors = staging / "setup-errors.log";
        const std::vector<std::string> args = {
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script.string(),
            "-PackageDir", bundle_dir, "-ComponentDir", staging.string(),
            "-ComponentCacheDir", cache.string(), "-DistroName", distro
        };
        check_cancel();
        bp::child child(powershell, bp::args(args), bp::std_out > output.string(),
                        bp::std_err > errors.string(), bp::windows::create_no_window);
        // A WSL import must finish before a canceled staging directory can be removed.
        // Cancellation is honored before publishing the new installation.
        child.wait();
        if (child.exit_code() != 0) {
            fs::ifstream stream(errors);
            std::string details((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
            if (details.size() > 8000) details = details.substr(details.size() - 8000);
            throw std::runtime_error("Runtime setup failed: " + details);
        }
        check_cancel();
        {
            fs::ofstream distro_file(staging / "slicer_linux_runtime_wsl_distro.txt");
            distro_file << distro;
            distro_file.close();
            fs::ofstream cache_file(staging / "slicer_linux_runtime_component_dir.txt");
            cache_file << cache.string();
            cache_file.close();
            if (!distro_file || !cache_file)
                throw std::runtime_error("Cannot save runtime configuration");
        }
        // Retain the old directory because a running Windows process may still map its DLL.
        if (fs::exists(target)) {
            fs::rename(target, previous);
            moved_previous = true;
        }
        fs::rename(staging, target);
        return true;
    } catch (const std::exception& e) {
        error = e.what();
        if (archive_open) close_zip_reader(&archive);
        boost::system::error_code ec;
        if (moved_previous) {
            fs::rename(previous, target, ec);
            if (ec) error += "; rollback failed: " + ec.message();
        }
        fs::remove_all(staging, ec);
        return false;
    }
}
} // namespace Slic3r
