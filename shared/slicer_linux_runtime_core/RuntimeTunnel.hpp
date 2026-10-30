#pragma once

#include "../../src/slic3r/GUI/Printer/BambuTunnel.h"

// Optional camera callbacks exposed by the OrcaStudio Linux component.
// Keep these additions private to the runtime rather than changing Alpha's
// BambuLib function table, whose layout belongs to its native camera loader.
extern "C" {
typedef struct __PlayerEventC {
    const char* event_name;
    const char* module;
    const char* phase;
    const char* result;
    const char* error_code;
    const char* error_message;
    const char* event_data_body;
} PlayerEventC;

typedef void (*TrackReporter)(void* context, const PlayerEventC* event);
typedef void (*StreamInfoCallback)(void* context, Bambu_StreamInfo* info);

typedef struct __Bambu_SessionStat {
    long long session_duration_ms;
    long long freeze_total_duration_ms;
    int freeze_count;
    float avg_fps;
    float avg_bitrate_kbps;
    float avg_jitter_ms;
    float max_jitter_ms;
} Bambu_SessionStat;
}
