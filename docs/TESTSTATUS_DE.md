# Test- und Kompatibilitätsstand

Stand der Veröffentlichung: 13.10.2026. Anwendung: `306d5e6dfec7834ec7fbebd16531b6156d8be657`.

## Automatisiert

Erfolgreicher [Windows-Build 37981590537](https://github.com/Noki3310/OrcaStudio/actions/runs/37981590537). Am 13.10.2026 erneut lokal ausgeführt:

| Prüfung | Ergebnis |
| --- | --- |
| HTTP-Anfragen einschließlich Abbruch/Null-Ausgabe | 15/15 |
| Düsenbefehle | 26/26 |
| Trocknungsbefehle, Fähigkeiten und Materialgrenzen | 49/49 |
| Trocknungsstatusübergänge | 12/12 |
| Runtime-Dispatcher | 6/6 |
| Vollständigkeitsprüfung Linux-Transport | Erfolgreich |

Insgesamt 108 gezielte Tests plus Transportprüfung. Mehrere Tests kompilieren Produktionsfunktionskörper gegen Testgeräte/Publisher. Sie sind keine Hardwareabnahme, keine umfassende Slicerprüfung und kein Test aller GUI-Interaktionen.

## Rückmeldungen vom realen Gerät

Diese Beobachtungen stammen vom Betreiber des Forks im X1C-/AMS-HT-Aufbau. Sie sind Erfahrungsnachweise; nicht jeder Test besitzt ein archiviertes Messprotokoll oder eine eindeutige Installer-Prüfsumme.

- Der zuvor beim Türöffnen beobachtete Absturz trat nach dem Patch nicht mehr auf.
- Trocknung am Drucker gestartet, anschließend aus Orca beendet: bestätigt.
- Trocknung aus der neueren Orca-Version gestartet: bestätigt, auch während der Drucker bereits im Druckablauf war.
- Filament wurde dabei als externe Spule/über Bypass gedruckt; der HT-Trockner lief weiter.

Daraus folgt ausdrücklich **kein Nachweis**, dass Heizen und aktives Fördern durch denselben HT gleichzeitig funktionieren. Eine angenommene Anfrage oder eine erhöhte Temperatur allein beweist ebenfalls keine Heizleistung.

## Noch zu prüfen

- Heizen und aktives Fördern durch denselben HT, einschließlich Start-/Stoppübergängen.
- Düsenänderung mit Kontrolle der tatsächlichen Geräterückmeldung in allen erlaubten/gesperrten Zuständen.
- Profil erstellen/laden/überschreiben/löschen und Persistenz nach Programmneustart.
- Alle GUI-Skalierungen, Fenstergrößen und Sprachkombinationen.
- Langzeitbetrieb und andere Firmware-/Druckerkombinationen.

Kein Standalone-Betrieb bei ausgeschaltetem X1C; kein ESP32-Protokollproxy in diesem Release. Bereits vorhandene Upstream-Funktionen für andere Drucker werden durch diese Liste nicht als neu getestet dargestellt.
