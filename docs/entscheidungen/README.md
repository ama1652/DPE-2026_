# Entscheidungsprotokoll (Vorlage C, Integrationspaket)

| Kennung | Datum | Frage | Entscheidung | Begründung | Betroffene Teams | Status |
|---|---|---|---|---|---|---|
| T2-001 | 08.11.2026 | Schnitt des Team-2-Prozesses in Teilprozesse | Hauptprozess + 6 Teilprozesse + gemeinsamer Baustein Kundenentscheidung | Method & Style (höchstens 10 Aktivitäten pro Ebene), Wiederverwendung der Freigabe für Team 1/3 | Team 2 (Baustein: alle) | Vorschlag |
| T2-002 | 08.11.2026 | Eine Instanz = ? | ein Nachversorgungsvorgang je Produkt und Pflegehaushalt | 1:1-Ausrichtung von Prozess- und Aktivitätsinstanz | alle | offen (Integrationskreis) |
| T2-003 | 17.11.2026 | Bestandsabfrage bei der Pflegeperson? | Entfällt. Team 2 führt den Ist-Bestand in der eigenen Datenbank, die Bedarfsermittlung liest ihn direkt. Damit entfällt die Pflicht-Ausnahme „Bestand nicht gemeldet“. | Feedback Prof. Stiehl beim Meilenstein | Team 2 | entschieden (Stiehl) |
| T2-004 | 17.11.2026 | Wie startet der Vorgang? | Zyklischer Timer-Start (alle 10 Tage), Nachrichtenstart aus der Pflege-App, bedingter Start „Bestand unterschritten“. Kein eigener Prüflauf, kein Esper-Start. | Feedback Prof. Stiehl beim Meilenstein | Team 2 | entschieden (Stiehl); Instanz-Zuordnung beim Timer offen |
| T2-005 | 17.11.2026 | Wie kommuniziert der Prozess mit der Pflegeperson? | Nur über Senden/Empfangen mit dem Blackbox-Pool „Pflege-App“, keine Benutzeraufgaben in der Tasklist | Feedback Prof. Stiehl: Die App ist ein eigenständiges System | Team 2, Team 1/3 (Kundenentscheidung) | Vorschlag an Team 1/3 |
