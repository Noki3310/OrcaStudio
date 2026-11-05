#pragma once

#include <atomic>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <string>

namespace Slic3r {

// Updated from the saved GUI preference only at startup, never mid-request.
inline std::atomic<bool>& runtime_network_preference()
{
    static std::atomic<bool> enabled{false};
    return enabled;
}

inline void set_runtime_network_preference(bool enabled)
{
    runtime_network_preference().store(enabled);
}

// Environment override remains available for diagnostics. Otherwise use the
// explicit, restart-required preference; native Alpha remains the default.
inline bool runtime_network_requested()
{
#ifdef _WIN32
    const char* value = std::getenv("ORCASTUDIO_USE_LINUX_RUNTIME");
    return value ? std::strcmp(value, "1") == 0 : runtime_network_preference().load();
#else
    return false;
#endif
}

#ifdef _WIN32
bool install_runtime_network_package(const std::string& archive_path,
                                     const std::string& bundle_dir,
                                     const std::function<bool()>& canceled,
                                     std::string& error);
#endif

} // namespace Slic3r
