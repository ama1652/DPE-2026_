# Team 2 – Benachrichtigungs-Worker (Story T2-11)

> **KI-Kennzeichnung (Kursregel):** Code erstellt mit Claude (Anthropic), Beginn und Ende stehen in jeder Datei. Verantwortlich: Saifudin Mohammadi.
>
> **Status:** Entwurf. Der Code ist gegen die APIs geprüft, aber **noch nicht mit Maven gebaut und nicht gegen eine laufende Engine getestet**. Das ist der nächste Schritt, sobald die Projektstruktur (T2-02, Mohammed) und die Umgebung (T2-01) stehen.

## Was er macht
Ein External-Task-Worker (Quarkus) holt drei Topics von CIB seven ab und schreibt die Nachricht in das **simulierte Postfach der Pflege-App** (Tabelle `t2_app_postfach`, Spalte `simulation = true`):

| Topic | Im Modell | Nachricht |
|---|---|---|
| `t2-freigabeanfrage-senden` | Kundenentscheidung → „Freigabeanfrage senden“ | Handlung, Grund, Folgen, Gültigkeit, Antwortmöglichkeiten |
| `t2-lieferbestaetigung-anfordern` | Lieferprüfung → „Lieferbestätigung anfordern“ | Bitte um Bestätigung: richtig, teilweise, falsch, nicht geliefert |
| `t2-ergebnis-mitteilen` | Hauptprozess → „Ergebnis mitteilen“ **und alle 5 Abbruch-Enden** | Ergebnis, Grund und bei Abbruch das **Reichweitenrisiko** („Vorrat reicht noch ca. X Tage“) |

Bei `t2-ergebnis-mitteilen` schreibt er zusätzlich den **Vorgangszustand** fort (Tabelle `t2_vorgang_status`: Zustand, Ergebnis, Grund). Das ist Stiehls Punkt 3: kein stummer Abbruch. Welches Ende erreicht wurde, erkennt er an der Element-ID (`End_Aufgeschoben` → „Bestellung aufgeschoben“ usw.).

**Fehler:** Die Retries zählen herunter (Standard 3, alle 10 s). Bei 0 Retries entsteht ein Incident im Cockpit.

## Aufbau (Panache im Repository-Stil)
| Klasse | Aufgabe |
|---|---|
| `BenachrichtigungsWorker` | Abo der 3 Topics (External Task Client), `complete` bzw. `handleFailure` |
| `BenachrichtigungsService` | Texte bauen, Postfach speichern, Vorgangszustand fortschreiben (`@Transactional`) |
| `AppNachricht` + `AppPostfachRepository` | simuliertes App-Postfach |
| `VorgangStatus` + `VorgangStatusRepository` | gemeinsamer Vorgangszustand (Integrationspaket 6.3) |

## Starten
```bash
export DB_URL=jdbc:mysql://localhost:3306/team2 DB_USER=team2 DB_PASSWORD=<lokal>
export ENGINE_REST_URL=http://localhost:8080/engine-rest
cd code/team2/benachrichtigung
mvn quarkus:dev
```
Zugangsdaten nur über Umgebungsvariablen, nie ins Repo.

## Offen / abstimmen
- **Mohammed (T2-02):** Modul in die gemeinsame Struktur (`worker`) übernehmen.
- **Erion (T2-03):** Tabellen `t2_app_postfach` und `t2_vorgang_status` mit dem gemeinsamen Datenmodell abgleichen.
- **Mohammed (T2-07):** Für das Reichweitenrisiko braucht der Worker `istBestand` und `verbrauchProTag` als Prozessvariablen. Die setzt „Verbrauch und Reichweite berechnen“ ohnehin für die DMN.
- Client: `org.camunda.bpm:camunda-external-task-client` 7.22 spricht die REST-API von CIB seven. Falls CIB seven einen eigenen Client vorschreibt, nur die Abhängigkeit tauschen.
