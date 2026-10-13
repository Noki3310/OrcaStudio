# OrcaStudio · X1C Community Edition

Independent community fork maintained by **Noki3310**, based on [jarczakpawel/OrcaStudio](https://github.com/jarczakpawel/OrcaStudio), Bambu Studio and OrcaSlicer. This is not an official release of any upstream project or Bambu Lab.

[Download Windows RC1](https://github.com/Noki3310/OrcaStudio/releases/tag/v02.08.01.55-x1c-de2-rc1) · [German documentation](../README.md) · [License](../LICENSE.txt)

Changes include the HTTP polling abort crash fix, idle X1C nozzle editing, bounded AMS HT drying controls, saved drying presets, drying-status corrections and additional German translations. The legacy drying path targets X1C firmware 01.09.01.00 with AMS HT/N3S.

User feedback confirms remote start/stop and drying while a print uses an external spool/bypass. **Heating and actively feeding through the same HT at the same time are not confirmed.** This release does not implement an ESP32 proxy or standalone drying with the printer switched off.

Windows networking requires WSL 2. Download the normal `.exe` installer and compare its SHA-256 with `SHA256SUMS.txt`. Application source: `306d5e6dfec7834ec7fbebd16531b6156d8be657`; successful build run: `37981590537`. The RC1 publication reuses that exact installer without recompilation. Full source, build recipes, provenance and license notices are provided alongside it. Other platform binaries are not part of this release.

Application license: GNU AGPL v3, with individual third-party licenses preserved. The proprietary Bambu networking plugin is obtained separately; this fork does not grant redistribution rights to it. See [third-party notices](../THIRD_PARTY_NOTICES.md) and [source/build details](BUILD_AND_SOURCE.md).
