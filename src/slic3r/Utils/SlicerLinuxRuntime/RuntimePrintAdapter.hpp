#pragma once

#include <stdexcept>
#include <string>
#include <utility>

namespace Slic3r::SlicerLinuxRuntime {

// Exact by-value layout used by the isolated 02.08.01 forwarder.
// Keep separate from Alpha's PrintParams, which appends queue_plate_id.
struct RuntimePrintParams {
    /* basic info */
    std::string     dev_id;
    std::string     task_name;
    std::string     project_name;
    std::string     preset_name;
    std::string     filename;
    std::string     config_filename;
    int             plate_index;
    std::string     ftp_folder;
    std::string     ftp_file;
    std::string     ftp_file_md5;
    std::string     nozzle_mapping;
    std::string     ams_mapping;
    std::string     ams_mapping2;
    std::string     ams_mapping_info;
    std::string     nozzles_info;
    std::string     connection_type;
    std::string     comments;
    int             origin_profile_id = 0;
    int             stl_design_id = 0;
    std::string     origin_model_id;
    std::string     print_type;
    std::string     dst_file;
    std::string     dev_name;

    /* access options */
    std::string     dev_ip;
    bool            use_ssl_for_ftp;
    bool            use_ssl_for_mqtt;
    std::string     username;
    std::string     password;

    /*user options */
    bool            task_bed_leveling;      /* bed leveling of task */
    bool            task_flow_cali;         /* flow calibration of task */
    bool            task_vibration_cali;    /* vibration calibration of task */
    bool            task_layer_inspect;     /* first layer inspection of task */
    bool            task_record_timelapse;  /* record timelapse of task */
    bool            task_timelapse_use_internal;
    bool            task_use_ams;
    std::string     task_bed_type;
    std::string     extra_options;
    int             auto_bed_leveling{ 0 };
    int             auto_flow_cali{ 0 };
    int             auto_offset_cali{ 0 };
    int             extruder_cali_manual_mode{ -1 };
    bool            task_ext_change_assist;
    bool            try_emmc_print;
    std::string     svc_context;
    std::string     slicer_uid;
};

// Reject unsupported queue requests before moving any caller-owned fields.
// Normal X1C print jobs preserve every field of the runtime ABI.
template<class AlphaPrintParams>
RuntimePrintParams to_runtime_print_params(AlphaPrintParams& input)
{
    if (!input.queue_plate_id.empty())
        throw std::invalid_argument("The 02.08.01 runtime does not support queued plate requests");
    RuntimePrintParams output{};
    output.dev_id = std::move(input.dev_id);
    output.task_name = std::move(input.task_name);
    output.project_name = std::move(input.project_name);
    output.preset_name = std::move(input.preset_name);
    output.filename = std::move(input.filename);
    output.config_filename = std::move(input.config_filename);
    output.plate_index = input.plate_index;
    output.ftp_folder = std::move(input.ftp_folder);
    output.ftp_file = std::move(input.ftp_file);
    output.ftp_file_md5 = std::move(input.ftp_file_md5);
    output.nozzle_mapping = std::move(input.nozzle_mapping);
    output.ams_mapping = std::move(input.ams_mapping);
    output.ams_mapping2 = std::move(input.ams_mapping2);
    output.ams_mapping_info = std::move(input.ams_mapping_info);
    output.nozzles_info = std::move(input.nozzles_info);
    output.connection_type = std::move(input.connection_type);
    output.comments = std::move(input.comments);
    output.origin_profile_id = input.origin_profile_id;
    output.stl_design_id = input.stl_design_id;
    output.origin_model_id = std::move(input.origin_model_id);
    output.print_type = std::move(input.print_type);
    output.dst_file = std::move(input.dst_file);
    output.dev_name = std::move(input.dev_name);
    output.dev_ip = std::move(input.dev_ip);
    output.use_ssl_for_ftp = input.use_ssl_for_ftp;
    output.use_ssl_for_mqtt = input.use_ssl_for_mqtt;
    output.username = std::move(input.username);
    output.password = std::move(input.password);
    output.task_bed_leveling = input.task_bed_leveling;
    output.task_flow_cali = input.task_flow_cali;
    output.task_vibration_cali = input.task_vibration_cali;
    output.task_layer_inspect = input.task_layer_inspect;
    output.task_record_timelapse = input.task_record_timelapse;
    output.task_timelapse_use_internal = input.task_timelapse_use_internal;
    output.task_use_ams = input.task_use_ams;
    output.task_bed_type = std::move(input.task_bed_type);
    output.extra_options = std::move(input.extra_options);
    output.auto_bed_leveling = input.auto_bed_leveling;
    output.auto_flow_cali = input.auto_flow_cali;
    output.auto_offset_cali = input.auto_offset_cali;
    output.extruder_cali_manual_mode = input.extruder_cali_manual_mode;
    output.task_ext_change_assist = input.task_ext_change_assist;
    output.try_emmc_print = input.try_emmc_print;
    output.svc_context = std::move(input.svc_context);
    output.slicer_uid = std::move(input.slicer_uid);
    return output;
}

} // namespace Slic3r::SlicerLinuxRuntime
