# OrcaStudio Alpha: X1C-Verbindung

Stand: 5. November 2026. Technischer Integrationsstand, keine vollständige Geräteabnahme.

## Ziel und Aufbau

Die vollständige Alpha-Codebasis einschließlich Python-Plug-in-System bleibt erhalten. Die ältere Bambu-Netzwerkschnittstelle wird über eine isolierte Runtime angebunden, statt ihre Datenstrukturen ungeprüft mit den neuen Alpha-Strukturen zu vermischen. Unter Windows verwendet diese Runtime WSL 2. Eine separat bediente Bambu-Connect-Anwendung ist für diesen Verbindungspfad nicht vorgesehen.

Die Alpha-Installation verwendet einen eigenen Installations- und Profilordner. Die stabile Veröffentlichung wird nicht ersetzt.

## Bedienung

In den Einstellungen im Bereich des Bambu-Netzwerk-Plug-ins gibt es unter Windows den Schalter „Experimentelle X1C-Verbindung verwenden“. Er wird gespeichert und erst beim nächsten Programmstart übernommen. Die normale Alpha-Verbindung bleibt standardmäßig ausgewählt.

Für Diagnosezwecke überschreibt ORCASTUDIO_USE_LINUX_RUNTIME die gespeicherte Auswahl: 1 aktiviert den Runtime-Pfad, jeder andere gesetzte Wert deaktiviert ihn. Ohne gesetzte Variable gilt die gespeicherte Auswahl. Andere Plattformen aktivieren diesen Windows-Pfad nicht.

Die Runtime benötigt eine funktionierende WSL-2-Installation. Die Einrichtung prüft die heruntergeladenen Linux-Komponenten und installiert die gebündelten Laufzeitdateien. Eine automatische Aktivierung fehlender Windows-Systemfunktionen ist noch nicht umgesetzt.

## Netzwerktransport

HTTP-Anfragen an die ausgewählten Bambu- und MakerWorld-Domänen können über dieselbe isolierte Runtime laufen. Andere Anbieter behalten den normalen HTTP-Pfad. Explizit native Downloads der Netzwerkkomponenten bleiben möglich, bevor die Runtime eingerichtet ist.

Der Adapter überträgt binäre Anfrageinhalte, Multipart-Metadaten, Dateiausschnitte, Zeitlimits, Statuscodes, Antwortheader und Abbruchanforderungen. Ungültige Dateiausschnitte und zu große Uploads werden vor dem Senden abgewiesen. Zeitlimits werden vor der Umrechnung begrenzt. Nicht erfolgreiche HTTP-Antworten führen zum Fehler-Callback.

Der Aufruf hält das Netzwerkmodul gegen paralleles Entladen fest und prüft die Runtime-ABI sowie den exportierten HTTP-Einstiegspunkt. Bambu-spezifische Zusatzheader bleiben auf die zugehörigen Anfragen beschränkt. Für die Linux-Verbindung werden passende Betriebssystemangaben verwendet.

## Verifikation und Build-Zuordnung

- Quellstand d49671b76c3617a4760a5364e340cdbbcc90979e: vollständiger Windows-Build einschließlich Installer erfolgreich, Actions-Lauf 42013933199.
- Installer-Artefakt dieses Laufs: 13415259685; ZIP-SHA256 0eba502ff9c3972d7f38e061e3912787d3b3ee0cd4e2c3f65ff558d46c920a7c.
- Dieser Installer enthält die HTTP-Anbindung, aber noch nicht den danach ergänzten Einstellungsschalter.
- Quellstand d40d479ead15fe5743545715b4cdddd920e76ac5 ergänzt Schalter, deutsche Texte, Header-Zuordnung und Auswahltests. Build dafür: Actions-Lauf 42069139404. Der Lauf wurde nach 90 Minuten während der Installation der Linux-Build-Abhängigkeiten abgebrochen; der Windows-Build wurde nicht gestartet.

Die Tests prüfen die produktive HTTP-Adapterfunktion mit einem ersetzten Transport: binäre Inhalte, Dateiausschnitte, fehlende Dateien, Größenbegrenzung, Zeitlimitüberlauf, Antwort-Callbacks und Abbruch. Die 15 bestehenden HTTP-Exporttests und der Alpha-Druckadaptertest bestanden ebenfalls. Der Auswahltest prüft Standardzustand, gespeicherte Auswahl, Umgebungsvariable und Plattformbegrenzung. Diese Tests ersetzen keinen Druckertest.

## Noch offene Abnahme

- Installation und Einrichtung auf einem frischen Windows-System.
- Vollständiger Login, Wiederanmeldung, Kamera und Druckübertragung am realen X1C.
- Vollständige Prüfung aller Alpha-Funktionen und installierbaren Python-Plug-ins in diesem Paket.
- Der ältere Runtime-Druckadapter weist Aufträge mit nicht leerem queue_plate_id ausdrücklich zurück. Im geprüften Alpha-Quellstand wird dieses Feld außerhalb von Definition und Adapter nicht gesetzt; daraus allein folgt keine fehlende sichtbare Warteschlangenfunktion.
- Vollständige deutsche Übersetzung aller Oberflächen und Hilfetexte.
- Prüfung aller Netzwerkaufrufe hinsichtlich gleichzeitigem Entladen und Callback-Lebensdauer.
- Die neue X1C-Firmware ist mit diesem Stand nicht praktisch abgenommen.

Trocknen während eines Drucks mit externer Spule/Bypass wurde vom Nutzer für die ältere Kombination bestätigt. Gleichzeitiger motorisierter Einzug und Trocknen aus demselben AMS HT wurde mit Fehler 1800-C06C 223520 abgelehnt. Diese Integration belegt keine Umgehung dieser Gerätebeschränkung.

## Bedeutung von „erfolgreich gebaut“

Ein erfolgreicher Build liefert einen prüfbaren Installer. Er bestätigt weder vollständige Funktionsgleichheit noch eine erfolgreiche Geräteabnahme. Bis diese Nachweise vorliegen, bleibt die Ausgabe ein Integrationsteststand.

## Ergänzungen für den nächsten Testinstaller

Kamera und Dateizugriff erhalten bei ausgewählter Runtime deren Source-Modul. Es wird kein zweites natives Windows-Modul gesucht und der geliehene Handle nicht doppelt freigegeben. Aktive Tunnel oder Callbacks verhindern das Entladen; vor dem Freigeben wird die Runtime heruntergefahren. Der Austausch einer laufenden Runtime erfordert einen Neustart. Der neue Regressionstest prüft diese Pfade mit den produktiven Methoden und einem simulierten Loader.

Die Einrichtung verlangt nun eine erfolgreiche Prüfung der heruntergeladenen Netzwerkkomponente. Fehler enthalten den Exitcode und die verfügbare Ausgabe des Einrichtungsprozesses und werden in der Oberfläche angezeigt. Anleitung und Gerätetestliste: [X1C_TESTANLEITUNG.md](X1C_TESTANLEITUNG.md).
