#include <nlohmann/json.hpp>
#include <cmath>
#include "DevFilaSystem.h"

#include "slic3r/GUI/DeviceManager.hpp"// TODO: remove this include
#include "DevUtil.h"

using namespace nlohmann;
namespace Slic3r
{

int DevFilaSystem::CtrlAmsReset() const
{
    json jj_command;
    jj_command["print"]["command"] = "ams_reset";
    jj_command["print"]["sequence_id"] = std::to_string(MachineObject::m_sequence_id++);
    return m_owner->publish_json(jj_command);
}

int DevFilaSystem::CtrlAmsStartDryingHour(int ams_id,
                                          std::string filament_type,
                                          int tag_temp,
                                          int tag_duration_hour,
                                          bool rotate_tray,
                                          int cooling_temp,
                                          bool close_power_conflict) const
{
    const auto* ams = GetAmsById(std::to_string(ams_id));
    if (!m_owner || !m_owner->is_connected() || !ams || !ams->IsSupportRemoteDry(m_owner)) return -1;
    if (tag_duration_hour < 1 || tag_duration_hour > 24 || tag_temp < 45 ||
        tag_temp > (ams->GetAmsType() == DevAmsType::N3S ? 85 : 65)) return -1;
    // Legacy Print & Dry uses actual loaded-material limits. Never relax a
    // reported interlock, force spool rotation or override a power conflict.
    if (!m_owner->is_support_remote_dry) {
        if (m_owner->is_in_calibration() || !IsPrintDryTemperatureAllowed(ams_id, tag_temp) ||
            !ams->GetDryStatus().has_value() ||
            (ams->GetDryStatus().value() != DevAms::DryStatus::Off &&
             ams->GetDryStatus().value() != DevAms::DryStatus::Cooling) || rotate_tray || close_power_conflict)
            return -1;
        const auto reasons = ams->GetCannotDryReason();
        if (reasons && !reasons->empty()) return -1;
    }
    json jj_command;
    jj_command["print"]["command"] = "ams_filament_drying";
    jj_command["print"]["sequence_id"] = std::to_string(MachineObject::m_sequence_id++);
    jj_command["print"]["ams_id"] = ams_id;
    jj_command["print"]["mode"] = static_cast<int>(DevAms::DryCtrlMode::OnTime); // Orca: cast scoped enum for json
    jj_command["print"]["filament"] = filament_type; // Orca: fix comma-operator typo
    jj_command["print"]["temp"] = tag_temp;
    jj_command["print"]["duration"] = tag_duration_hour;
    jj_command["print"]["humidity"] = 0;
    jj_command["print"]["rotate_tray"] = rotate_tray;
    jj_command["print"]["cooling_temp"] = cooling_temp;
    jj_command["print"]["close_power_conflict"] = close_power_conflict;
    return m_owner->publish_json(jj_command);
}

bool DevFilaSystem::IsPrintDryTemperatureAllowed(int ams_id, int temperature) const
{
    if (!m_owner) return false;
    if (!m_owner->is_in_printing() && !m_owner->is_in_printing_pause()) return true;
    const auto* ams = GetAmsById(std::to_string(ams_id));
    if (!ams) return false;
    bool has_material = false;
    for (const auto& entry : ams->GetTrays()) {
        const auto* tray = entry.second;
        if (!tray) return false;
        if (!tray->is_exists) continue;
        has_material = true;
        if (!tray->is_tray_info_ready()) return false;
        const auto preset = tray->get_ams_drying_preset();
        if (!preset) return false;
        const auto limit = preset->filament_dev_ams_drying_temperature_on_print.find(ams->GetAmsType());
        if (limit == preset->filament_dev_ams_drying_temperature_on_print.end()) return false;
        for (float value : {limit->second, preset->filament_dev_drying_softening_temperature,
                           preset->filament_dev_ams_drying_heat_distortion_temperature}) {
            if (!std::isfinite(value) || value <= 0 || temperature > value) return false;
        }
    }
    // Unknown/empty material must not silently inherit the selected UI preset.
    return has_material;
}

int DevFilaSystem::CtrlAmsStopDrying(int ams_id) const
{
    const auto* ams = GetAmsById(std::to_string(ams_id));
    if (!m_owner || !m_owner->is_connected() || !ams || !ams->IsSupportRemoteDry(m_owner)) return -1;
    json jj_command;
    jj_command["print"]["command"] = "ams_filament_drying";
    jj_command["print"]["sequence_id"] = std::to_string(MachineObject::m_sequence_id++);
    jj_command["print"]["ams_id"] = ams_id;
    jj_command["print"]["mode"] = static_cast<int>(DevAms::DryCtrlMode::Off); // Orca: cast scoped enum for json
    jj_command["print"]["filament"] = ""; // Orca: fix comma-operator typo
    jj_command["print"]["temp"] = 0;
    jj_command["print"]["duration"] = 0;
    jj_command["print"]["humidity"] = 0;
    jj_command["print"]["rotate_tray"] = false;
    jj_command["print"]["cooling_temp"] = 0;
    jj_command["print"]["close_power_conflict"] = false;
    return m_owner->publish_json(jj_command);
}

}
