# Team 2 – Prozesslogik-Worker (Stories T2-07, T2-08, T2-10)

> **KI-Kennzeichnung (Kursregel):** Code erstellt mit Claude (Anthropic), Beginn und Ende stehen in jeder Datei. Verantwortlich: Saifudin Mohammadi (von Mohammed übernommen).
>
> **Status:** Die Rechenregeln (`Rechner`) sind lokal geprüft. Das Modul ist gegen die APIs kompiliert, aber **noch nicht mit Maven gebaut und nicht gegen eine laufende Engine getestet**.

## Topics

| Topic | Im Modell | Liest | Setzt |
|---|---|---|---|
| `t2-vorgang-pruefen` | Hauptprozess „Laufenden Vorgang prüfen“ | Business Key | `vorgangOffen` (läuft schon eine Instanz mit gleichem Key? REST `process-instance/count`) |
| `t2-reichweite-berechnen` | Hauptprozess „Verbrauch und Reichweite berechnen“ | Versorgungsprofil, letzte 2 Bestände | `istBestand`, `bestandMenge`, `verbrauchProTag`, `tageBisPruefung`, `lieferzeitTage`, `mindestbestand`, `zielbestand`, `verbrauchssprung`, `reichweiteTage` (Eingaben der DMN „Nachversorgungsbedarf“) |
| `t2-vorschlag-erstellen` | Bestellfreigabe „Produkt und Menge vorschlagen“ | Profil, Produkt, Bestand, `ersatzGrund`, `anzahlVorschlaege` | `bestellvorschlag` (JSON), `produktHinterlegt`, `produktGewechselt`, `lieferantGewechselt`, `preisGesamt`, `preisgrenze`, `bestellmenge`, `zielbestand`, `freigabeHandlung`, `freigabeFolgen` (Eingaben der DMN „Berechtigungsregel“) |
| `t2-ersatzoption-pruefen` | Bestellabwicklung „Ersatzoption prüfen“ | `bestellvorschlag`, `anzahlBestellversuche` | `ersatzMoeglich` (Ersatz hinterlegt, verfügbar, höchstens 2 Versuche) |
| `t2-bestand-fortschreiben` | Hauptprozess „Bestand und Verbrauch fortschreiben“ | `bestellvorschlag` | neuer Bestandseintrag, `istBestand`, `reichweiteTage` |

Die beiden Regelaufgaben laufen als DMN direkt in der Engine (`decisionRef`), dafür gibt es keinen Worker.

## Regeln (Projektannahmen)
- Bestellmenge = Zielbestand − Ist-Bestand, aufgerundet auf volle Packungen
- Verbrauchssprung, wenn der beobachtete Verbrauch zwischen den letzten zwei Bestandseinträgen ≥ 1,5 × Verbrauchsannahme ist
- Ersatzprodukt beim 2. Vorschlag (Änderungswunsch) oder wenn `ersatzGrund` gesetzt ist, nur die im Profil hinterlegte Option
- Haushalt und Produkt kommen aus den Variablen oder aus dem Business Key `PH-0001:TP-M`. **Jede Instanz muss mit Business Key starten.**

## Starten
```bash
export DB_URL=jdbc:mysql://localhost:3306/team2 DB_USER=team2 DB_PASSWORD=<lokal>
export ENGINE_REST_URL=http://localhost:8080/engine-rest
mysql -u team2 -p team2 < ../../../testdaten/team2/T2_Testdaten.sql
cd code/team2 && mvn -pl prozesslogik quarkus:dev
```

## Abstimmen
- **Erion (T2-03):** Die Entities `Versorgungsprofil`, `Produkt`, `Lieferant`, `Bestand` (Tabellen wie in den Testdaten) gehören später ins Modul `persistenz`.
- **Amar (T2-14):** `bestellvorschlag` ist ein JSON-String mit `produktId`, `produktName`, `lieferantId`, `packungen`, `stueck`, `preisGesamt`.
