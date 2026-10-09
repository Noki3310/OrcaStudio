# X1C controls test build

Based on p6 plus the HTTP polling-abort fix. Windows artifact names end in
`-x1c-controls-de2` to distinguish this installer from the HTTP-only build.

## Nozzle settings

Device > Printer Parts restores type and diameter editing for a connected,
idle X1 Carbon. Choose the physically installed nozzle and Apply. The command
is the legacy `system.set_accessories` payload from OrcaSlicer v2.3.1
(`src/slic3r/GUI/DeviceManager.cpp`, `command_set_printer_nozzle`).
Only hardened/stainless steel and 0.2/0.4/0.6/0.8 mm are offered. No device
state is changed optimistically: the printer must report the selected value.
Flow type remains read-only. Other printers are unchanged.

## AMS HT drying

Click the AMS HT humidity/drying indicator in Device. Use the existing drying
dialog for material, temperature (45–85 C), duration (1–24 hours), Start and Stop.
Existing filament temperature limits and reported interlocks remain in effect.

The compatibility gate is intentionally restricted to X1 Carbon firmware
01.09.01.00 with AMS HT (N3S). A real drying-status report is required before
opening the controls. The firmware's remote-drying capability bit is not changed.
Experimental drying requests during printing are enabled on this legacy path.
X1C firmware support is NOT confirmed. Start is available during a
print or pause when every loaded tray has a known drying preset and the requested
temperature meets its on-print, softening and heat-distortion limits. An empty feeder does not block standalone spool drying. Unknown material in an
occupied feeder still blocks the print-time request. Calibration, reported interlocks, spool
rotation and power-conflict override remain blocked. Stop remains available
while printing. Use the existing Start/Stop buttons; no separate firmware command
or automatic restart when the firmware stops drying is introduced. Actual
simultaneous printing and heating still need confirmation on X1C hardware. The regular capability-advertised path remains supported.

The wire command is the existing `print.ams_filament_drying` implementation.
Independent reference: https://github.com/maziggy/bambuddy, functions
`send_drying_command` in `backend/app/services/bambu_mqtt.py` and the X1C firmware
table in `backend/app/services/printer_manager.py`. This is supporting source
evidence, NOT a real-device acceptance test of this build.

Publish errors are displayed. Start waits for actual status; an unchanged idle
state times out after about 30 seconds. A sent/acknowledged command alone is not
proof that the heater started. Firmware rejection cannot be fixed by changing
only the UI. The printer and original heating/safety controls remain required.

## Validation

`python3 tools/slicer_linux_runtime/test_nozzle_settings.py` compiles the actual
nozzle-command body against a fake publisher (26 cases).
`python3 tools/slicer_linux_runtime/test_drying_controls.py` compiles the actual
capability gate and drying-command bodies against fake devices (49 cases).
These run in CI with the existing 15 HTTP and 6 dispatcher tests and transport
verification before the full Windows build. They do not test real firmware,
electrical hardware, or GUI rendering.

Manual acceptance is still required: install the new installer; check 0.6 mm
Apply against the printer display and refreshed print dialog; open AMS HT drying,
choose material-appropriate settings, start and verify heating on the AMS display,
then Stop and verify the real device changes state (cooldown may continue).
Also verify disconnects/calibration block new starts and rejection gives a message.
For Print & Dry, start a print with an identified heat-resistant filament, open
the HT drying dialog and choose a temperature within its print limits. Verify
that both feeding and heating continue on the real device; then test Stop.
Unknown material in an occupied feeder and temperatures above its material
limits must block Start. An unoccupied feeder must allow standalone drying,
including while a print uses another source, subject to reported interlocks.


## German UI and user profiles (de2)

Completed 420 previously empty German catalog entries and 50 source/UI additions.
The general Start translation no longer says Start calibration. Drying buttons
explicitly say Start drying. Nozzle controls explain print/calibration/disconnect
locks and refresh their visibility without reopening the dialog.

Drying labels update independently of graphics. Active drying with an absent or
unknown substatus remains Drying; cooling, stopping, errors and unknown states
are distinct. Temperature alone never implies heating. The dialog is resizable,
and hours use a translated label with a non-collapsing input field.

Own drying profiles save a name, material ID, temperature and hours in AppConfig.
Select a material and values, use Save profile as; reusing the name updates after
confirmation, a new name creates a copy. Delete requires confirmation. Loading
never sends a command or changes the AMS material assignment. Existing command
limits are rechecked on Start. Profiles whose material is unavailable cannot load.

Hardware feedback on 2026-10-09: user confirmed Stop in Orca ended drying started
on the printer. Start remains unconfirmed; the disabled button in the screenshot
was a local print-time material guard, not evidence of firmware rejection.

Validation: 12 compiled production status-label transitions, 49 command cases,
26 nozzle cases and gettext format/coverage checks. Full GUI rendering, profile
persistence after restarting Orca, and device behavior need installer acceptance.
Test profile create/load/update/delete with German names, confirm settings survive
restart, check unknown/over-limit feedstock remains blocked, and test the empty
feeder while printing elsewhere. No firmware capability is fabricated.
