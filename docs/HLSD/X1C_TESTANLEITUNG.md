# OrcaStudio Alpha: Test am X1C

Dies ist eine Vorabversion für die Geräteprüfung. Sie enthält die Alpha-Codebasis mit Python-Plug-ins und den experimentellen direkten Bambu-Verbindungspfad. Eine separat gestartete Bambu-Connect-Anwendung ist dafür nicht vorgesehen. Die erfolgreiche Kompilierung ersetzt keine Prüfung am Drucker.

## Einrichtung unter Windows

1. Den Installer aus dieser Veröffentlichung ausführen. Die Anwendung heißt **OrcaStudio Alpha** und verwendet den eigenen Profilordner **OrcaStudioAlpha**.
2. Die vorhandene OrcaStudio-Installation kann für den Vergleich erhalten bleiben. Zum Test jeweils nur eine der beiden Anwendungen verwenden.
3. Für die experimentelle Verbindung muss **WSL 2** auf Windows funktionieren. Bei noch nicht installiertem WSL in einer PowerShell mit Administratorrechten `wsl --install --no-distribution` ausführen und Windows anschließend neu starten. Bei vorhandenem WSL den Zustand mit `wsl --status` prüfen. Die eigene OrcaStudio-Linux-Umgebung wird bei der Runtime-Einrichtung importiert.
4. In OrcaStudio Alpha die Einstellungen öffnen und im Bereich **Bambu network plug-in** den Schalter **Experimentelle X1C-Verbindung verwenden** aktivieren. Die Anwendung neu starten.
5. Das angebotene Netzwerk-Plug-in herunterladen und installieren. Die Einrichtung prüft die Linux-Komponenten und die gebündelte Runtime. Erscheint ein Fehler, zeigt der Dialog technische Details. Nicht von einer erfolgreichen Einrichtung ausgehen, solange dieser Schritt fehlschlägt.
6. OrcaStudio Alpha nach der Einrichtung neu starten und mit dem Bambu-Konto anmelden. Drucker und AMS müssen anschließend mit aktuellen Statuswerten erscheinen.

Wenn ORCASTUDIO_USE_LINUX_RUNTIME auf dem Rechner gesetzt wurde, überschreibt diese Diagnosevariable den Schalter. Für normale Tests sollte sie nicht gesetzt sein.

Microsoft-Anleitung zur WSL-Installation und den Befehlen: https://learn.microsoft.com/en-us/windows/wsl/basic-commands

## Prüfablauf

| Schritt | Prüfung | Erwartung |
| --- | --- | --- |
| 1 | Start und Schließen | Kein Absturz; Einstellungen bleiben gespeichert. |
| 2 | Bambu-Anmeldung | Konto wird angemeldet; der eigene X1C erscheint. |
| 3 | Neustart | Verbindung und Anmeldung werden wiederhergestellt. |
| 4 | Status und Kamera | Aktuelle Temperaturen/Status; Kamerabild lässt sich starten und beenden. |
| 5 | Gerätedateien | Dateiliste lässt sich öffnen, ohne Hänger oder Absturz. |
| 6 | Kleiner Druckauftrag | Slicen, übertragen und drucken; Fortschritt stimmt mit dem Drucker überein. |
| 7 | Drucksteuerung | Pause, Fortsetzen und Stop werden am Drucker tatsächlich ausgeführt. |
| 8 | AMS HT im Leerlauf | Passendes Material/Temperatur wählen; Start, Restzeit, Status und Stop am HT vergleichen. |
| 9 | Eigene Trocknungsprofile | Speichern, erneut wählen, ändern und löschen. |
| 10 | Düsendaten | Nur bei passendem Gerätezustand ändern; Anzeige am Drucker vergleichen. |
| 11 | Alpha-Plug-ins | Gewünschtes Python-Plug-in installieren, öffnen und nach Neustart erneut verwenden. |
| 12 | Verbindungsunterbrechung | Außerhalb eines Drucks Netzwerk kurz trennen; Wiederverbindung und Status prüfen. |

Für eine Fehlermeldung notieren: Schritt, genauer Wortlaut, Uhrzeit, Drucker-Firmware, Verbindungsart und Quellstand dieser Veröffentlichung. Zugangscodes und Tokens nicht öffentlich posten.

## Bekannte Grenzen

- Kein Nachweis für gleichzeitiges Trocknen und motorisiertes Fördern aus demselben AMS HT. Die bekannte Ablehnung des Geräts wird nicht umgangen.
- Aufträge mit dem neueren Feld queue_plate_id werden vom älteren Runtime-Druckadapter abgewiesen. Normale Druckaufträge verwenden dieses zusätzliche Feld nicht.
- Die komplette deutsche Übersetzung ist noch nicht abgeschlossen; technische Diagnoseausgaben können Englisch enthalten.
- Die Windows-Systemvoraussetzung WSL 2 wird nicht stillschweigend aktiviert.
- Die Runtime kann im laufenden Programm nicht über die normale Plug-in-Neuladefunktion ausgetauscht werden. Dafür OrcaStudio neu starten.
- Kamera, Anmeldung und Druckübertragung sind softwareseitig angebunden, aber ihre praktische Abnahme für diese Version erfolgt erst mit diesem Test.
- Diese Vorabversion ist keine Bestätigung der Kompatibilität mit einer neueren X1C-Firmware.

## Zurück zur normalen Verbindung

Den experimentellen Schalter ausschalten und OrcaStudio neu starten. Damit wird wieder der normale Alpha-Netzwerkpfad verwendet. Alternativ die bisherige stabile OrcaStudio-Installation starten.

## Prüfsumme

Die Datei SHA256SUMS.txt gehört genau zum mitgelieferten Installer. Zum Vergleich in PowerShell:

```powershell
Get-FileHash .\OrcaStudio-Alpha-Integration-Test-Setup.exe -Algorithm SHA256
```
