# X1C controls test build

Based on p6 plus the HTTP polling-abort fix. Windows artifact names end in
`-x1c-controls` to distinguish this installer from the HTTP-only build.

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
On this legacy path, starting is limited to an idle printer without calibration;
spool rotation and power-conflict override are disabled. Stop remains available
while printing. The regular capability-advertised path remains supported.

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
capability gate and drying-command bodies against fake devices (30 cases).
These run in CI with the existing 15 HTTP and 6 dispatcher tests and transport
verification before the full Windows build. They do not test real firmware,
electrical hardware, or GUI rendering.

Manual acceptance is still required: install the new installer; check 0.6 mm
Apply against the printer display and refreshed print dialog; open AMS HT drying,
choose material-appropriate settings, start and verify heating on the AMS display,
then Stop and verify the real device changes state (cooldown may continue).
Also verify disconnects/printing block new starts and rejection gives a message.
