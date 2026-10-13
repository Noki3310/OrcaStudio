# Lizenzen und Fremdkomponenten

## Anwendung

OrcaStudio wird hier als modifizierter Fork unter der GNU Affero General Public License, Version 3, gemäß der unveränderten Datei [LICENSE.txt](LICENSE.txt) weitergegeben. Copyright-Vermerke und individuelle Lizenzangaben in den Quelldateien bleiben bestehen. Änderungsstand und Datum sind in [CHANGELOG.md](CHANGELOG.md) dokumentiert. Die Gewährleistungsregelungen ergeben sich aus der jeweiligen Lizenz.

## Bibliotheken und Ressourcen

`deps/`, `deps_src/`, `resources/`, `tests/` und weitere Unterverzeichnisse enthalten Komponenten mit eigenen Lizenztexten. Die AGPL des Hauptprogramms ersetzt deren Bedingungen nicht. Die mitgelieferten Lizenz-/Copyright-Dateien und Header sind maßgeblich. Buildrezepte in `deps/*/*.cmake` nennen Bezugsquellen, Versionen und, soweit vorhanden, Prüfsummen der externen Quellen.

Die Release-Datei `OrcaStudio_Licenses.zip` sammelt die im Repository vorhandenen Lizenztexte sowie Copyright-Dateien aus der mitgelieferten Ubuntu-Laufzeit. Sie ist ein ergänzender Überblick und ersetzt die Hinweise in den Originalquellen nicht. `runtime-packages.tsv` ordnet die im WSL-Abbild enthaltenen Ubuntu-Binärpakete ihren Quellpaketen und Versionen zu. Die zugehörigen Quellen sind über Ubuntu/Launchpad verfügbar; der Release-Prozess dokumentiert die Zuordnung.

## Linux-Laufzeit

Der Windows-Installer enthält eine Ubuntu-24.04-basierte WSL-Laufzeit und den offenen OrcaStudio-Runtime-Host. Ubuntu-Pakete unterliegen ihren jeweiligen Lizenzen; deren Hinweise liegen im Abbild unter `/usr/share/doc/*/copyright` und `/usr/share/common-licenses`. Das Abbild wird durch die Skripte unter `tools/slicer_linux_runtime/rootfs/` erzeugt. Buildablauf und Herkunft stehen in [BUILD_AND_SOURCE.md](docs/BUILD_AND_SOURCE.md).

## Bambu-Netzwerkplugin

Das proprietäre `bambu_networking`-Plugin wird nicht durch diese AGPL-Lizenz neu lizenziert. Laut Upstream wird es nicht im OrcaStudio-Paket ausgeliefert, sondern bei Bedarf gesondert bezogen. Der Release-Prozess prüft die vorhandenen Installer-/Runtime-Dateinamen auf ein versehentlich mitgepacktes Bambu-Netzwerkplugin und bricht dann ab. Eine vollständige rechtliche Prüfung aller Kombinationen mit externen Plugins wird damit nicht behauptet. Es werden keine Weitergaberechte für dieses Plugin eingeräumt.

## Quellen

- [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html)
- [GNU-Lizenz-FAQ](https://www.gnu.org/licenses/gpl-faq.html)
- [Ubuntu-Quellpakete](https://launchpad.net/ubuntu/+source)
- [Ursprung und Autoren](AUTHORS.md)

Bei der Weitergabe von Binärdateien müssen der zugehörige Quellcode und die erforderlichen Lizenzinformationen zugänglich bleiben. Ein Link auf einen beweglichen Entwicklungszweig ersetzt die Zuordnung zum tatsächlichen Build nicht. Die bereitgestellte Zuordnung beschreibt den geprüften technischen Veröffentlichungsstand, keine pauschale rechtliche Zertifizierung.
