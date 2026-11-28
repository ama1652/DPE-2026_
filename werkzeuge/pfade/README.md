# Pfade selbst durchgehen (Team 2)

> Verantwortlich: Amar

Mit `pfad.py` spielt man eine Instanz von `T2_Materialversorgung` Schritt für Schritt durch CIB seven und entscheidet an jedem Haltepunkt selbst, welchen Weg sie nimmt. Das Skript übernimmt die Rollen, die es **noch nicht** gibt: Worker, Lieferant, Pflege-App und Team 3. Die einzige Benutzeraufgabe („Grenzfall prüfen“) erledigt man selbst in der Tasklist.

So kann jeder alle 19 Pfade des Modells (100 % der Elemente und Flüsse aller 5 Prozesse) im Cockpit nachvollziehen, auch bevor die echten Teile fertig sind.

| Datei | Wozu |
|---|---|
| `pfad.py` | das Skript, braucht nur Python 3 ohne Zusatzpakete |
| `pfad.cmd` | Windows: startet `pfad.py` und lädt beim ersten Mal ein portables Python |
| PDFs `00_Start_hier.pdf` + `P01…P19` | Anleitung mit Screenshots für jeden Schritt. **Nicht im Git** (70 MB), bekommt ihr von Amar |

## 1. Einmalig einrichten

### Mac (Amar, Erion)

1. Docker Desktop installieren und starten.
2. CIB seven starten. Das ist dieselbe Version wie auf den Screenshots in den PDFs:
   ```bash
   docker run -d --name cibseven -p 127.0.0.1:8080:8080 cibseven/cibseven:tomcat-2.2.0
   ```
   Später reicht `docker start cibseven`. Nach etwa 30 s antwortet `http://localhost:8080/webapp/` (Login `demo` / `demo`).
3. Terminal im Ordner `werkzeuge/pfade` des Repos öffnen und eingeben:
   ```bash
   python3 pfad.py einrichten
   ```

### Windows (Saifudin, Mohammed)

1. CIB seven über Saifudins Startskript starten: `werkzeuge\start\cib_starten.cmd` doppelklicken, siehe [`werkzeuge/start/README.md`](../start/README.md). **Das CIB-seven-Fenster offen lassen.**
   Das Skript startet nebenbei schon eine Instanz. Die stört nicht, sie wartet einfach.
2. Im Explorer zum Ordner `werkzeuge\pfade` gehen, oben in die Adressleiste `cmd` tippen und Enter drücken. Dann öffnet sich ein Konsolenfenster genau in diesem Ordner.
3. Dort eingeben:
   ```
   pfad einrichten
   ```
   Beim ersten Mal lädt `pfad.cmd` ein portables Python nach `Dokumente\DPE-Werkzeuge\python` (ca. 10 MB, es wird nichts installiert).
   In PowerShell statt cmd heißt es `.\pfad einrichten`.

> **Achtung:** Saifudins Skript lädt **CIB seven Run 3.0.0**, die PDFs zeigen **2.2.0**. Die Abläufe sind gleich. Ob die Oberfläche bei 3.0.0 an einzelnen Stellen anders aussieht, ist noch nicht geprüft. Wer Unterschiede findet: bitte an Amar melden.

`einrichten` deployt alle 5 BPMN und 2 DMN aus `prozesse/team2` und legt die Gruppe `pruefstelle` an, mit `demo` als Mitglied. Ohne diese Gruppe sieht man „Grenzfall prüfen“ nicht in der Tasklist.

## 2. Befehle

Die PDFs zeigen die Mac-Befehle. Unter Windows schreibt man statt `python3 pfad.py` einfach `pfad`.

| Mac | Windows | Was passiert |
|---|---|---|
| `python3 pfad.py einrichten` | `pfad einrichten` | Modelle deployen und Gruppe anlegen |
| `python3 pfad.py start` | `pfad start` | neue Instanz über die Nachricht „Bestand manuell gemeldet“ |
| `python3 pfad.py start bedingt` | `pfad start bedingt` | Start über die Bedingung „Bestand unterschritten“ |
| `python3 pfad.py start timer` | `pfad start timer` | Start über den Timer „Prüftermin erreicht“, sofort ausgelöst |
| `python3 pfad.py weiter` | `pfad weiter` | pausierte Instanz weiterspielen (Pause mit `q` oder Strg+C) |
| `python3 pfad.py weiter <id>` | `pfad weiter <id>` | eine beliebige Instanz übernehmen, z. B. eine, die die echte Pflege-App gestartet hat |
| `python3 pfad.py status` | `pfad status` | zeigt, wo die Instanz gerade steht |
| `python3 pfad.py aufraeumen` | `pfad aufraeumen` | löscht **alle** laufenden Team-2-Instanzen (fragt vorher) |
| `… --wahl 1,1,2,…` | `… --wahl 1,1,2,…` | spielt einen Pfad automatisch ab (Tabelle unten) |
| `… --alles-simulieren` | `… --alles-simulieren` | ignoriert die Liste `ECHT` und simuliert wieder alles (siehe 3.) |
| `… --details` | `… --details` | zeigt alle Elemente, alle Variablen und IDs statt der Kurzfassung |

**So liest man die Ausgabe:**

```
   Was passiert ist:
     ✓ Verbrauch und Reichweite berechnen   [echter Worker]  Verbrauchssprung: nein, Reichweite Tage: 7, Bestand: 30
     ✓ Nachversorgungsbedarf feststellen    [DMN]            nachbestellen: ja
     » hinein in Teilprozess Bestellfreigabe
     ✓ Produkt und Menge vorschlagen        [echter Worker]  Vorschlag: Testprodukt M, 3 Pck., 74,70 €
   Stand: Bestand 30 · Reichweite 7 Tage · Vorschlag Testprodukt M, 3 Pck., 74,70 € · Freigabe AUTOMATISCH · Bestellversuch 1

━━ Schritt 1: Bestellung übermitteln (Bestellabwicklung, Teilprozess)
   In echt: …
   1) Erledigt melden …
```

- **Was passiert ist:** alles seit deiner letzten Eingabe, eine Zeile pro Aufgabe mit dem Ergebnis. In Klammern steht, wer die Aufgabe erledigt hat: `[echter Worker]`, `[pfad.py]` (noch simuliert), `[DMN]`, `[Tasklist]` oder `[Nachricht]`. Hat sich ein Wert geändert, steht der alte Wert in Klammern dahinter („vorher …“). `»` und `«` zeigen, wann die Instanz in einen Teilprozess hinein- und wieder hinausgeht, `⏰` eine abgelaufene Frist.
- **↳ (Begründung):** Bei Rechnungen und Regeln steht darunter, wie das Ergebnis zustande kam, z. B. `↳ Abweichung: Preis 79,20 € > Grenze 75,00 € · Ersatzprodukt → KUNDENFREIGABE`. `pfad.py` rechnet das aus den gesetzten Variablen nach (Funktion `warum`).
- **Stand:** die wichtigsten Werte der Instanz. Die Zeile erscheint nur, wenn sich etwas geändert hat.
- **Schritt N:** Hier entscheidest du. „In echt“ sagt, wer das später übernimmt. Schritte, die ein echter Worker erledigt, bekommen keine eigene Überschrift.

## 3. Wie es weitergeht, wenn echte Teile fertig werden

`pfad.py` ist ein **Platzhalter**. Mit jedem fertigen Worker oder Nachrichten-Sender fällt ein Stück Simulation weg. Dafür gibt es oben in `pfad.py` die Liste `ECHT`:

```python
ECHT = {
    "t2-vorgang-pruefen",               # Worker Prozesslogik (Saifudin, #7)
    "Lieferant_Bestellantwort_Team2",   # Camel leitet die Lieferantenantwort weiter (Amar, #15/#16)
}
```

- Steht ein **Topic** (External Task) oder ein **Nachrichtenname** in `ECHT`, simuliert `pfad.py` an dieser Stelle nichts mehr. Es zeigt „pfad.py simuliert hier nichts und wartet …“ und läuft weiter, sobald der echte Teil fertig ist. Meldet der echte Worker einen Fehler (Incident), bricht es mit der Fehlermeldung ab.
- Alles, was **nicht** in `ECHT` steht, simuliert `pfad.py` wie bisher.
- Hat ein echter Worker eine Aufgabe gerade gesperrt, wartet `pfad.py` auch dann, wenn das Topic nicht in `ECHT` steht.
- Welche Namen möglich sind, steht in `pfad.py` in den Tabellen `TOPICS` (External Tasks) und `NACHRICHTEN`.

### Ablauf im Team (Regel)

1. Jeder arbeitet wie bisher in **seinem eigenen Branch pro Issue**.
2. Wer seinen Worker oder Sender fertig hat, trägt im **selben Pull Request** das Topic bzw. den Nachrichtennamen in `ECHT` ein, eine Zeile pro Eintrag mit Kommentar (wer, welches Issue).
3. Vor dem PR einmal durchspielen: echten Worker starten, dann `pfad start` und einen Pfad bis zum Ende spielen, der über das eigene Topic läuft. Im Cockpit prüfen, dass die Instanz richtig weiterläuft.
4. Nach dem Merge zeigt `main` immer den aktuellen Stand: Was in `ECHT` steht, ist echt, alles andere wird noch simuliert. Teilweise fertige Arbeit (z. B. nur der Start oder nur Saifudins Worker) kann also jederzeit rein.
5. Ändert sich ein Topic- oder Nachrichtenname im Modell, wird `pfad.py` (`TOPICS` / `NACHRICHTEN`) im selben PR angepasst.

### Einen bestimmten Pfad erzwingen

Ein echter Worker entscheidet nach den Daten in der Datenbank, nicht nach der Auswahl im Terminal. Einen bestimmten Pfad bekommt man dann
- über passende Testdaten, oder
- mit `--alles-simulieren`. Dabei **müssen die echten Worker aus sein**, sonst schnappen sie sich die Aufgaben.

## 4. Alle 19 Pfade (für automatische Läufe)

Gilt für den Stand **ohne** Einträge in `ECHT`. Sobald etwas in `ECHT` steht, fallen dort Eingaben weg, dann mit `--alles-simulieren` laufen lassen (echte Worker aus).

| Pfad | Start | `--wahl` | erwartetes Ende |
|---|---|---|---|
| P01 Happy Path | `start` | `1,1,1,1,1,1,1,1,1,1,1` | End_Abgeschlossen |
| P02 Bestand reicht noch | `start` | `1,2` | End_Ausreichend |
| P03 Vorgang läuft schon | `start` | `2` | End_Offen |
| P04 Zu teuer, Kunde gibt frei | `start` | `1,1,2,1,1,1,1,1,1,1,1,1,1` | End_Abgeschlossen |
| P05 Kunde lehnt ab | `start` | `1,1,2,1,2,1` | End_NichtFreigegeben |
| P06 Kunde schiebt auf | `start` | `1,1,2,1,3,1` | End_Aufgeschoben |
| P07 Kunde antwortet nie | `start` | `1,1,2,1,5,1,5,1` | End_NichtFreigegeben |
| P08 Kunde will 3× ändern | `start` | `1,1,2,1,4,2,1,4,2,1,4,1` | End_NichtFreigegeben |
| P09 Prüfstelle: nicht zulässig | `start` | `1,1,3,NICHT_ZULAESSIG,1` | End_NichtZulaessig |
| P10 Verbrauchssprung, Prüfstelle holt Kundenfreigabe | `start` | `1,3,1,KUNDENFREIGABE,1,1,1,1,1,1,1,1,1,1` | End_Abgeschlossen |
| P11 Ersatz-Schleife | `start` | `1,1,1,1,2,1,1,1,1,1,1,1,1,1,1` | End_Abgeschlossen |
| P12 Nicht verfügbar, kein Ersatz | `start` | `1,1,1,1,2,2,1` | End_KeineBestellung |
| P13 Lieferant antwortet nie | `start` | `1,1,1,1,3,1,3,2,1` | End_KeineBestellung |
| P14 Teillieferung, Nachlieferung kommt | `start` | `1,1,1,1,1,1,1,2,1,1,1,1,1` | End_Abgeschlossen |
| P15 Falschlieferung bleibt ungeklärt | `start` | `1,1,1,1,1,1,1,3,1,2,1,1` | End_Ungeklaert |
| P16 Pflegeperson und Team 3 antworten nie | `start` | `1,1,1,1,1,1,1,4,1,3,1,1` | End_Ungeklaert |
| P17 Versandmeldung kommt nie | `start` | `1,1,1,1,1,2,1,1,1,1,1` | End_Abgeschlossen |
| P18 Start über Bedingung | `start bedingt` | `1,2` | End_Ausreichend |
| P19 Start über Timer | `start timer` | `1,2` | End_Ausreichend |

Beispiel: `python3 pfad.py start --wahl 1,2` bzw. `pfad start --wahl 1,2`. Am Ende steht `FERTIG: Hauptprozess endet in '… (End_…)'`.
Bei P09/P10 erledigt das Skript im automatischen Lauf auch die Tasklist-Aufgabe selbst.

## 5. Probleme

| Problem | Lösung |
|---|---|
| „CIB seven nicht erreichbar“ | Mac: `docker start cibseven`, 30 s warten. Windows: `cib_starten.cmd` nochmal starten, CIB-Fenster offen lassen |
| „Grenzfall prüfen“ fehlt unter „My Group Tasks“ | `einrichten` ausführen. Wenn man die Aufgabe schon zugewiesen hat, liegt sie unter „My Tasks“ |
| „Aufgabe war schon gesperrt“ | Es läuft ein echter Worker auf demselben Topic. Entweder das Topic in `ECHT` eintragen oder den Worker beenden |
| „wartet …“ und nichts passiert | Der echte Worker oder Sender für diesen Schritt läuft nicht. Starten oder mit Strg+C pausieren |
| Windows: komische Zeichen wie `←[1m` | Konsole ist zu alt. Windows Terminal benutzen oder `set NO_COLOR=1` |
| Umlaute im Formular „Grenzfall prüfen“ kaputt („PrÃ¼fergebnis“) | Bekannt (generiertes Formular). Die Werte kommen trotzdem richtig an |

## 6. Hinweise für Claude und andere KI-Assistenten

Wer mit einem Assistenten am Repo arbeitet: Dieser Abschnitt ist für ihn geschrieben.

- `pfad.py` ist ein **Test-Hilfsmittel, kein Produktivcode**. Es ersetzt per REST (`fetchAndLock`/`complete`, `POST /message`, `POST /condition`, Timer-Jobs ausführen) die Teile, die noch fehlen.
- **Nur Python-Standardbibliothek.** Unter Windows läuft es mit dem portablen Embedded-Python, dort gibt es kein `pip`. Keine Zusatzpakete einbauen.
- Wird ein Worker oder Sender fertig: Topic bzw. Nachrichtenname in `ECHT` eintragen (eine Zeile, Kommentar mit Name und Issue), und zwar **im selben PR** wie der Worker. Nicht die Simulation in `TOPICS`/`NACHRICHTEN` löschen. Die braucht `--alles-simulieren` weiterhin.
- Die Begründungen (`warum` in `pfad.py`) bilden die Regeln aus `prozesse/team2/DMN.md` und `code/team2/prozesslogik/README.md` nach. Ändert sich dort eine Regel (Grenzen, Reihenfolge, Formel), `warum` im selben PR anpassen.
- Werden im Modell (`prozesse/team2`) Topics, Nachrichten, Variablen oder Wege geändert: `TOPICS`/`NACHRICHTEN` in `pfad.py` und die Tabelle in Abschnitt 4 anpassen. Danach alle 19 Pfade automatisch laufen lassen (Tabelle in Abschnitt 4, mit `--alles-simulieren`, falls `ECHT` nicht leer ist). Jeder Lauf muss mit dem erwarteten `End_…` enden.
- **Nie** echte Worker und `pfad.py --alles-simulieren` gleichzeitig auf denselben Topics laufen lassen.
- `aufraeumen` löscht **alle** laufenden Team-2-Instanzen. Nicht ungefragt ausführen. Einzelne Testinstanzen gezielt per `DELETE /process-instance/<id>` löschen.
- Die PDFs werden außerhalb des Repos gebaut (bei Amar) und zeigen CIB seven 2.2.0. Ändert sich das Modell, sind die Screenshots veraltet. Dann Amar Bescheid geben, statt die PDFs ins Repo zu legen.
