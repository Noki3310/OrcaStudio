# Build, Quellcode und Zuordnung

## Unveränderter Anwendungsbuild

- Anwendung: `306d5e6dfec7834ec7fbebd16531b6156d8be657`.
- Basis vor den lokalen X1C-Anpassungen: `bef044f40bb957bd0967378705fc24ae20655c45`.
- [Windows-Build](https://github.com/Noki3310/OrcaStudio/actions/runs/37981590537): erfolgreich.
- Installer-Artefakt: ID `11649267493`, `OrcaStudio_Windows_V02.08.01.55-x1c-controls-de2_installer`.
- SHA-256 des GitHub-Artefakt-ZIP: `7416b638951783dae28d1962c652e8576d58b6bb5570fd29f1650662fb947c50`. Dies ist **nicht** die Prüfsumme der enthaltenen EXE.
- Die Prüfsumme der tatsächlichen EXE wird beim Veröffentlichen neu berechnet und in `SHA256SUMS.txt` gespeichert.

Der Release-Tag zeigt auf den Anwendungsquellstand. Später ergänzte Veröffentlichungsdokumente und Verpackungsskripte liegen auf `main`; ihr Commit wird im `release-manifest.json` separat erfasst. Der Installer wird weder neu kompiliert noch umetikettiert.

## Quellen herunterladen

Das Asset `OrcaStudio_Source_306d5e6d.tar.gz` enthält den vollständigen Git-Baum dieses Anwendungsstands einschließlich `deps/`, `deps_src/`, Buildskripten und Lizenzdateien. Es enthält keine nachträglich heruntergeladenen externen Dependency-Archive und keinen Quellcode des proprietären Bambu-Plugins.

```bash
git clone https://github.com/Noki3310/OrcaStudio.git
cd OrcaStudio
git checkout 306d5e6dfec7834ec7fbebd16531b6156d8be657
```

## Buildablauf

Die maßgebliche automatisierte Anleitung steht in `.github/workflows/build_windows_bridge.yml` **am genannten Anwendungscommit**. Sie erstellt zunächst auf Ubuntu 24.04 den Linux-Runtime-Host und das WSL-Abbild, überträgt diese in den Windows-Build und erstellt dort mit MSVC/CMake und NSIS den Installer. Ein isoliertes Ausführen nur des Windows-Slicer-Builds ersetzt diese Runtime-Vorbereitung nicht.

Windows: `build_release_vs.bat deps`, danach `build_release_vs.bat slicer` und im Buildordner `cpack -G NSIS`. Versionsdefinition: `version.inc`. Linux-Runtime: `tools/slicer_linux_runtime_host/` und `tools/slicer_linux_runtime/rootfs/`. Die Tests sind in `tools/slicer_linux_runtime/README_x1c_controls.md` aufgeführt.

Dependency-Quellen und Hashes stehen in den CMake-Rezepten unter `deps/`; eingebundene Quellen unter `deps_src/`. Die ursprüngliche Buildkette verwendet teilweise bewegliche Runner-/Paketversionen. Daher wird kein bitidentischer Neubau zugesichert. Der archivierte Originalinstaller und sein SHA-256-Wert identifizieren die tatsächlich veröffentlichte Datei.

## Laufzeitpakete und Lizenzunterlagen

`runtime-packages.tsv` enthält die Paket-/Quellversionszuordnung des tatsächlichen WSL-Abbilds. `runtime-source-links.tsv` nennt die versionsbezogenen Ubuntu/Launchpad-Quellseiten. Die dazugehörigen Lizenztexte werden in `OrcaStudio_Licenses.zip` übernommen. `dependency-recipes.txt` enthält die Bezugsrezepte der externen Anwendungsabhängigkeiten.

Beim Weiterverteilen bleiben die jeweiligen Quellcodepflichten zu beachten. Die Archive und Quellverweise sollen zusammen mit dem Installer erhalten bleiben; sie sind keine Behauptung, dass das Hauptquellarchiv allein sämtliche Ubuntu-/Drittquellen enthält.
