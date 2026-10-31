#pragma once

#include <array>
#include <limits>
#include <optional>
#include <string>
#include <nlohmann/json.hpp>

namespace Slic3r {

struct NetworkPluginResource {
    std::string version;
    std::string url;
};

inline std::optional<std::array<unsigned, 4>> parse_network_package_version(const std::string& text)
{
    std::array<unsigned, 4> parts{};
    size_t pos = 0;
    for (size_t part = 0; part < parts.size(); ++part) {
        const size_t start = pos;
        while (pos < text.size() && text[pos] >= '0' && text[pos] <= '9') {
            const unsigned digit = static_cast<unsigned>(text[pos++] - '0');
            if (parts[part] > (std::numeric_limits<unsigned>::max() - digit) / 10)
                return std::nullopt;
            parts[part] = parts[part] * 10 + digit;
        }
        if (pos == start)
            return std::nullopt;
        if (part != parts.size() - 1 && (pos == text.size() || text[pos++] != '.'))
            return std::nullopt;
    }
    return pos == text.size() ? std::make_optional(parts) : std::nullopt;
}

// The endpoint can return multiple resources. Never substitute another ABI series
// just because it appears last or has a larger version number.
inline std::optional<NetworkPluginResource> select_network_plugin_resource(
    const std::string& body, const std::string& requested_version)
{
    const auto requested = parse_network_package_version(requested_version);
    if (!requested)
        return std::nullopt;
    const auto response = nlohmann::json::parse(body, nullptr, false);
    if (!response.is_object() || !response.contains("message") ||
        response["message"] != "success" || !response.contains("resources") ||
        !response["resources"].is_array())
        return std::nullopt;

    std::optional<NetworkPluginResource> selected;
    std::array<unsigned, 4> selected_version{};
    for (const auto& entry : response["resources"]) {
        if (!entry.is_object() || !entry.contains("version") || !entry["version"].is_string() ||
            !entry.contains("url") || !entry["url"].is_string())
            continue;
        const auto version = entry["version"].get<std::string>();
        const auto parsed = parse_network_package_version(version);
        const auto url = entry["url"].get<std::string>();
        if (!parsed || (*parsed)[0] != (*requested)[0] || (*parsed)[1] != (*requested)[1] ||
            (*parsed)[2] != (*requested)[2] || url.compare(0, 8, "https://") != 0 || url.size() <= 8)
            continue;
        if (!selected || selected_version < *parsed) {
            selected = NetworkPluginResource{version, url};
            selected_version = *parsed;
        }
    }
    return selected;
}

} // namespace Slic3r
