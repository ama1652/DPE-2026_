# Startanleitung Team 2 (T2-20)

> Verantwortlich: Saifudin Mohammadi

Mit diesen Skripten kann jeder im Team die Tests laufen lassen und die Modelle auf CIB seven deployen. Es braucht **kein Git, kein Java, kein Maven und kein Docker**. Beim ersten Start laden die Skripte Java 21, Maven 3.9.11 und CIB seven Run 3.0.0 portabel nach `Dokumente\DPE-Werkzeuge`.

## Voraussetzungen
- Windows 10 oder 11 mit Internet
- Das Repo als Ordner auf dem PC: auf GitHub **Code → Download ZIP**, entpacken (oder `git clone`)

## 1. Tests ausführen
1. Im Repo-Ordner `werkzeuge\start` auf **`tests_starten.cmd`** doppelklicken.
   - Falls Windows warnt: „Weitere Informationen“ → „Trotzdem ausführen“.
2. Warten. Beim ersten Mal dauert es 10–15 Minuten (Downloads), danach etwa 1 Minute.
3. Ergebnis: `testergebnis.txt` auf dem Desktop.

Erwartet:

| Prüfung | Ergebnis |
|---|---|
| `werkzeuge/dmn-test` | 6 Tests, BUILD SUCCESS |
| `werkzeuge/endzustand-test` | 16 Tests (jeder Endzustand eine Zeile `OK  End_…`), BUILD SUCCESS |
| `code/team2` | RechnerTest 5 Tests, BUILD SUCCESS |

## 2. CIB seven starten und Modelle deployen
1. In `werkzeuge\start` auf **`cib_starten.cmd`** doppelklicken.
2. Es öffnet sich ein zweites Fenster, in dem CIB seven läuft. **Dieses Fenster offen lassen.**
3. Das Skript deployt alle 5 BPMN- und 2 DMN-Dateien aus `prozesse/team2` und startet eine Instanz mit Business Key `PH-0001:TP-M` über die Nachricht `PflegeApp_Bestandsmeldung_Team2`.
4. Ergebnis: `cib_ergebnis.txt` auf dem Desktop.

Erwartet: 5 Prozesse und 2 DMN deployt, Instanz gestartet, sie wartet an „Laufenden Vorgang prüfen“ (`t2-vorgang-pruefen`). Weiter läuft sie erst, wenn die Worker aus `code/team2` laufen (brauchen die Datenbank, T2-03).

## 3. Cockpit ansehen
- Im Browser `http://localhost:8080` öffnen (CIB-seven-Fenster muss offen sein).
- Anmelden mit `demo` / `demo` (Standard der lokalen Installation).
- Cockpit → Prozesse → `T2_Materialversorgung`: Dort steht die wartende Instanz im Diagramm.
- `invoice` und `ReviewInvoice` sind das Beispiel, das CIB seven mitbringt.

## Probleme
| Problem | Lösung |
|---|---|
| Fenster schließt sich sofort | Nicht die `.ps1` doppelklicken, sondern die `.cmd`-Datei |
| „CIB seven antwortet nicht“ | Läuft schon etwas auf Port 8080? Anderes Programm beenden und neu starten |
| Deploy meldet weniger als 5 Prozesse | `cib_ergebnis.txt` zeigt die Antwort der Engine, damit ins Team |
| Alles neu laden | Ordner `Dokumente\DPE-Werkzeuge` löschen und Skript neu starten |
