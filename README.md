# OrcaStudio · X1C Community Edition

Deutschsprachiger Community-Fork von [OrcaStudio](https://github.com/jarczakpawel/OrcaStudio), gepflegt von **Noki3310**. Schwerpunkt sind die Bedienung des **Bambu Lab X1 Carbon mit Firmware 01.09.01.00**, AMS-HT-Trocknungssteuerung und deutsche Bedienoberflächen.

**Unabhängiges Community-Projekt. Keine offizielle Veröffentlichung von Bambu Lab, OrcaSlicer oder dem ursprünglichen OrcaStudio-Projekt.**

## Download

**[Windows-Installer und Versionshinweise](https://github.com/Noki3310/OrcaStudio/releases/tag/v02.08.01.55-x1c-de2-rc1)** · [Installation](docs/INSTALLATION_DE.md) · [Änderungen](CHANGELOG.md) · [Teststand](docs/TESTSTATUS_DE.md) · [English](docs/README_EN.md)

Die erste Veröffentlichung ist eine **Vorabversion (RC1)**. Empfohlen ist die Datei `OrcaStudio_Windows_Installer_V02.08.01.55-x1c-controls-de2.exe`. WSL 2 ist für die Windows-Netzwerkanbindung erforderlich. Für diese Edition werden zunächst nur Windows-Installationsdateien angeboten; macOS und Linux sind nicht als eigene Release-Binaries geprüft.

## Was dieser Fork ergänzt

- Korrektur eines Nullzeigerzugriffs beim Abbruch von HTTP-Abfragen im Linux-Runtime-Forwarder. Der zuvor beim Türöffnen beobachtete Absturz trat nach dem Patch im Nutzertest nicht mehr auf.
- Düsentyp und Düsendurchmesser für den verbundenen, untätigen X1C wieder im Gerätebereich ändern. Während Druck, Kalibrierung oder fehlender Verbindung gelten Sperren; der Durchflusstyp bleibt nur lesbar.
- AMS-HT-Trocknung über Orca starten und stoppen, Temperatur und Dauer einstellen, abhängig vom gemeldeten Gerätezustand und den Materialgrenzen.
- Eigene Trocknungsprofile mit Name, Materialkennung, Temperatur und Stunden speichern, laden, aktualisieren und löschen.
- Trocknungsstatus besser unterscheiden: Trocknen, Abkühlen, Stoppen, Fehler und unbekannte Zustände. Temperatur allein gilt nicht als Heiznachweis.
- Deutsche Übersetzungen ergänzt; der Trocknungsbutton heißt nicht mehr „Kalibrierung starten“.
- Trocknen bei unbesetztem HT-Einzug ermöglichen, soweit Gerätestatus und Schutzbedingungen dies zulassen. Ein unbekanntes Material im belegten Einzug wird dadurch nicht freigegeben.

Die ursprüngliche Linux-Netzwerkbrücke und WSL-Integration stammen aus dem vorgelagerten OrcaStudio-Projekt. Details zur Herkunft stehen in [AUTHORS.md](AUTHORS.md) und im [bewahrten Upstream-README](docs/upstream/README.md).

## Was bestätigt ist und was noch offen ist

| Funktion | Stand |
| --- | --- |
| Windows-Build einschließlich Installer | GitHub Actions erfolgreich, Quellstand `306d5e6d` |
| Türöffnungsabsturz nach Patch | Laut Nutzerrückmeldung nicht mehr aufgetreten |
| Trocknung vom Drucker aus starten und über Orca stoppen | Vom Nutzer bestätigt |
| Trocknung über Orca starten | Vom Nutzer bestätigt |
| Trocknung läuft während Druck mit externer Spule/Bypass weiter | Vom Nutzer bestätigt |
| Gleichzeitig trocknen und aktiv aus demselben HT fördern | **Nicht bestätigt** |
| Trocknungsprofile und Bedienoberfläche: weitere Praxistests stehen noch aus. | Noch offen |
| Standalone-Trocknung bei ausgeschaltetem X1C | **Nicht Bestandteil dieses Forks** |

Der Legacy-Kompatibilitätspfad ist im Code auf X1C-Firmware **01.09.01.00** und AMS HT (**N3S**) begrenzt. Andere Firmwarestände sind dadurch nicht automatisch unterstützt. Die normale geräteseitig gemeldete Trocknungsunterstützung bleibt bestehen. Es wird keine Druckerfirmware verändert und kein fehlender Status als Erfolg ausgegeben.

## Bedienung

- **Düse:** Gerät → Drucker-Teile. Nur die tatsächlich eingebaute Düse auswählen und die Rückmeldung des Druckers kontrollieren.
- **Trocknung:** Im Gerätebereich die Feuchtigkeits-/Trocknungsanzeige des AMS HT öffnen. Material, Temperatur und Stunden auswählen; Start und Stopp beziehen sich auf den ausgewählten HT.
- **Zoom zur Maus:** Einstellungen → Steuerung → Kamera → „Zum Mausposition zoomen“. Diese Funktion war bereits vorhanden; für diese Veröffentlichung wurde kein Zoom-Patch benötigt.

## Fehler melden und mitarbeiten

[Fehler melden](https://github.com/Noki3310/OrcaStudio/issues/new/choose). Bitte Build, Windows-Version, Drucker-/HT-Firmware, Filamentquelle und konkrete Schritte angeben. Zugangscodes, Tokens, Kontodaten und Seriennummern vor dem Hochladen aus Logs entfernen. [Hinweise zur Mitarbeit](CONTRIBUTING.md).

## Lizenz und Quellcode

Die Anwendung bleibt unter der **GNU AGPL v3** gemäß [LICENSE.txt](LICENSE.txt). Vorhandene Copyright- und Lizenzvermerke bleiben erhalten. Fremdkomponenten haben eigene Lizenzbedingungen; siehe [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Exakter Anwendungsquellstand des Installers](https://github.com/Noki3310/OrcaStudio/tree/306d5e6dfec7834ec7fbebd16531b6156d8be657) · [Build und Quellen](docs/BUILD_AND_SOURCE.md) · [Datenschutz und Netzwerk](docs/PRIVACY_DE.md)

Das proprietäre Bambu-Netzwerkplugin gehört nicht zum offenen Quellcode dieses Forks. Die Upstream-Architektur lädt es bei Bedarf separat. Dieser Fork erteilt dafür keine eigenen Nutzungs- oder Weitergaberechte.
