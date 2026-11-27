# Endzustand-Test (Story T2-06)

> **KI-Kennzeichnung:** Erstellt mit Claude (Anthropic). Verantwortlich: Saifudin Mohammadi (von Mohammed übernommen).

Deployt alle 5 BPMN- und 2 DMN-Dateien in eine Camunda-7-Engine im Speicher (CIB seven ist ein Fork von Camunda 7) und spielt **jeden Endzustand des Hauptprozesses** durch: 16 Testfälle wie in `testdaten/team2` (TF01–TF16). Die Worker werden simuliert, Nachrichten und Timer löst der Test selbst aus.

```bash
cd werkzeuge/endzustand-test
mvn test
```

Erwartet: 16 Tests grün, je Fall eine Zeile `OK  End_…`. **Noch nicht ausgeführt** (Maven war in der KI-Umgebung gesperrt) – bitte einmal lokal laufen lassen und das Ergebnis ins Issue #6 schreiben.
