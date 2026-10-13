# Installation unter Windows

## Voraussetzungen

Windows x64 mit funktionsfähigem WSL 2 und aktivierter Hardwarevirtualisierung. Diese Veröffentlichung enthält einen normalen Installer, keine Verpflichtung zur Nutzung einer portablen Version. Ein bestehendes Profil-/Konfigurationsbackup vor einem Versionswechsel erleichtert die Rückkehr zur vorherigen Installation.

## Installation

1. Unter [Releases](https://github.com/Noki3310/OrcaStudio/releases/tag/v02.08.01.55-x1c-de2-rc1) den Windows-Installer `.exe` und `SHA256SUMS.txt` herunterladen.
2. Optional die Datei in PowerShell prüfen: `Get-FileHash .\OrcaStudio_Windows_Installer_V02.08.01.55-x1c-controls-de2.exe -Algorithm SHA256`. Mit dem Eintrag für genau diese Datei vergleichen. Ein SHA-256-Wert ist keine Herausgebersignatur.
3. OrcaStudio schließen und den Installer ausführen. Keine Druckerfirmware wird mit diesem Installer aktualisiert.
4. OrcaStudio starten. Die Netzwerkanbindung verwendet die eigene WSL-Distribution `BambuStudio-LinuxRuntime`. Beim ersten Start kann deren Einrichtung Zeit benötigen.
5. Gewünschte Sprache, Druckerprofil und Verbindung kontrollieren. Vorhandene Geräteberechtigungen/Zugangsdaten werden weiterhin benötigt.

Wenn WSL 2 fehlt, in einer administrativen PowerShell die Windows-Funktionen aktivieren und anschließend Windows neu starten:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Danach mit `wsl --status` kontrollieren. Gegebenenfalls WSL aktualisieren (`wsl --update`). Virtualisierung muss im BIOS/UEFI aktiviert sein. Der Installer ist ein Community-Build; eine vertrauenswürdige Herausgebersignatur wird nicht zugesichert. Schutzfunktionen nicht global deaktivieren.

## Erste Kontrolle

- Buildkennung: `02.08.01.55-x1c-controls-de2`; Veröffentlichung: `v02.08.01.55-x1c-de2-rc1`.
- Düse nur bei untätigem, verbundenem Drucker passend zur eingebauten Hardware ändern und echte Rückmeldung abwarten.
- AMS-HT-Trocknungsdialog öffnen, materialgerechte Temperatur/Dauer wählen. Heizbetrieb und Stopp am Gerät überprüfen; Abkühlung kann nach Stopp weiterlaufen.
- Der Legacy-Pfad ist für X1C 01.09.01.00 und HT N3S begrenzt. Kein Firmwarewechsel wird hier empfohlen oder benötigt, wenn diese Kombination bereits vorliegt.
- Mauszoom: Einstellungen → Steuerung → Kamera → „Zum Mausposition zoomen“ aktivieren.

## Rückkehr und Entfernen

Die vorherige Installer-Datei aufbewahren. Zum Zurückwechseln OrcaStudio schließen und die gewünschte Version installieren; Profilkompatibilität vorher mit einer Sicherung absichern. Die Deinstallation der Anwendung und das Löschen der WSL-Distribution sind getrennte Vorgänge. Die WSL-Distribution nicht löschen, wenn noch benötigte Daten darin liegen; eine Deinstallation soll keine anderen WSL-Distributionen entfernen.
