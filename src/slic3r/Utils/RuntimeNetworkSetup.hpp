#pragma once

#include <cstdlib>
#include <cstring>
#include <functional>
#include <string>

namespace Slic3r {

// Keep the experimental transport explicit until cloud and device acceptance tests pass.
inline bool runtime_network_requested()
{
#ifdef _WIN32
    const char* value = std::getenv("ORCASTUDIO_USE_LINUX_RUNTIME");
    return value && std::strcmp(value, "1") == 0;
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
