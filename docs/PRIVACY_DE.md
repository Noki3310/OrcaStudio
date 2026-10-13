# Netzwerk und Datenschutz

Dieser Fork übernimmt die Netzwerkarchitektur von OrcaStudio. Für die Druckerkommunikation kann das externe Bambu-Netzwerkplugin verwendet werden. Je nach gewähltem Verbindungsmodus werden lokale Druckerverbindungen und/oder Bambu-Dienste genutzt. Ein Cloud-Login ist kein reiner Offlinebetrieb.

Die Windows-Ausgabe verwendet dafür eine lokale WSL-Linux-Laufzeit, einschließlich lokaler Authentifizierungs-/Browserkomponenten. Diese Veröffentlichung ergänzt keinen eigenen Telemetriedienst von Noki3310. Eine Aussage über sämtliche Datenverarbeitung des externen Plugins oder der Bambu-Dienste wird damit nicht getroffen.

Profile und Anwendungseinstellungen werden lokal gespeichert. Trocknungsprofile enthalten unter anderem Name, Materialkennung, Temperatur und Dauer. Zugangsdaten und Geräteinformationen können in Konfigurationen und Diagnoseausgaben vorkommen. Vor öffentlichen Fehlerberichten Logs auf Zugangscodes, Tokens, Kontodaten, Seriennummern und private Netzwerkdaten prüfen.

GitHub-Issues sind öffentlich. Keine Geheimnisse dort posten. Für den Umgang mit Kontodaten gelten zusätzlich die Bedingungen der jeweils verwendeten Dienste.
