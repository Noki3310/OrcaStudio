# Änderungen

## v02.08.01.55-x1c-de2-rc1 · 13.10.2026

Erste öffentliche Community-Vorabversion von Noki3310. Anwendung auf Basis OrcaStudio p6, Versionskennung des vorhandenen Windows-Installers `02.08.01.55-x1c-controls-de2`. Die Release-Kennung RC1 ordnet diesem unveränderten Installer Dokumentation und Prüfsummen zu; es wurde dafür keine neue Anwendungsversion kompiliert.

### Anwendung: Quellstand 306d5e6dfec7834ec7fbebd16531b6156d8be657

- `4f4e92bc`: HTTP-Polling-Abbruch ohne Nullzeigerzugriff; zusätzliche Regressionstests.
- `401bab77`: Windows-Build für den Patchzweig aktiviert.
- `2d18f75e`: X1C-Düsentyp/-durchmesser im zulässigen Gerätezustand wieder bearbeitbar; AMS-HT-Trocknung über begrenzten Legacy-Kompatibilitätspfad.
- `dc01184d`: Trocknungsanforderungen während Druck/Pause unter Materialgrenzen; keine Spulenrotation und kein Überschreiben von Leistungskonflikten auf diesem Pfad.
- `306d5e6d`: Start- und Statuskorrekturen, gespeicherte Trocknungsprofile, unbesetzter Einzug als zulässiger Fall, deutsche Übersetzungen und verständlichere Sperrhinweise. 420 zuvor leere deutsche Katalogeinträge sowie weitere UI-Texte ergänzt. Das ist keine Zusicherung, dass jeder zur Laufzeit mögliche Text aus Drittkomponenten deutsch ist.

### Veröffentlichungsunterlagen

Deutsche Projektseite, englische Kurzbeschreibung, Installation, Testmatrix, Quellcode-/Buildzuordnung, Herkunfts- und Lizenzhinweise, Fehler-/Funktionsvorlagen, Release-Manifest, SHA-256-Prüfsummen und automatisierter Veröffentlichungsablauf ergänzt. Das bisherige Upstream-README bleibt unter `docs/upstream/README.md` erhalten.

### Grenzen

Nutzertests bestätigen Start/Stopp und Trocknung parallel zum Druck mit externer Spule/Bypass. Gleichzeitiges Heizen und aktiver Vorschub aus demselben HT sowie Standalone-Betrieb sind nicht bestätigt. Der ESP32-Proxy und das Gehäuse gehören nicht zu diesem Software-Release. [Ausführlicher Teststand](docs/TESTSTATUS_DE.md).
