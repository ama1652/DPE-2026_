# Team 2 Materialversorgung – Product Backlog

> **KI-Kennzeichnung:** Erstellt mit Claude (Anthropic) aus Teamauftrag 2, Projektvorgaben, Projekthandbuch, Integrationspaket und unserem BPMN-Modell (`prozesse/team2`). Vom Team zu bestätigen.
>
> **Aufgabenbrett:** jede Story ist ein [GitHub Issue](https://github.com/mohammadisaifuddin187-dev/DPE-2026_/issues) mit gleicher Nummer (T2-05 = #5), Labels `epic: …` / `wer: …`, Meilenstein = Sprint.
>
> **Stand:** 27.11.2026 (Mohammeds Stories T2-02, 06–10 an Saifudin übergeben) · Format wie in TerraMax: *Als … möchte ich …, damit …* + Akzeptanzkriterien. Punkte nach Fibonacci (1, 2, 3, 5, 8).

## Sprints

| Sprint | Zeitraum | Ziel |
|---|---|---|
| **S1** | 17.11.–30.11.2026 | Umgebung steht, jede Komponente läuft für sich. Statusrunde Ende November |
| **S2** | 01.12.–14.12.2026 | **Meilenstein 2:** Happy Path Ende zu Ende (Timer-Start bis „Nachversorgung abgeschlossen“) |
| **S3** | 15.12.2026–Jan. 2027 | Ausnahmewege, Probelauf mit Team 1/3, Pitch, Abgabe (Code + DB-Abzug) |

## Verteilung (Punkte je Person)

| Person | Schwerpunkt | Punkte S1+S2 |
|---|---|---|
| **Amar** | Messaging, Integration und Eventing (Camel, ActiveMQ, Lieferant-Simulation, Esper) | 26 |
| **Erion** | Persistenz, REST, Pflege-App-Simulation, bedingter Start | 16 |
| **Mohammed** | – (erste Fassung der DMN geliefert, Stories am 27.11. an Saifudin übergeben) | 0 |
| **Saifudin** | Benachrichtigung, Testdaten, Doku, Schnittstelle Kundenentscheidung, BPMN; **seit 27.11. auch** External-Task-Worker, DMN, Deploy auf CIB seven | 34 |

## Definition of Done (für jede Story)
- Der Code liegt im Repo und hat den Kommentar `// Verantwortlich: <Name>`. Der KI-Anteil ist mit Beginn, Ende und Werkzeug gekennzeichnet (Projektvorgaben).
- Die Story läuft lokal mit den Testdaten. Die Schritte stehen in der Startanleitung.
- Eine zweite Person hat den Pull Request angesehen und kann den Code erklären.
- Keine Passwörter oder echten Daten im Repo.

---

## Epic E1 – Arbeitsumgebung

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-01 | Als **Entwicklerteam** möchten wir eine gemeinsame lokale Umgebung (JDK 17, Quarkus, CIB seven, ActiveMQ Classic, MySQL), damit alle Komponenten zusammen laufen. | Alle 4 starten die Umgebung nach derselben Anleitung · Versionen stehen in der README | 3 | **alle** | S1 |
| T2-02 | Als **Entwicklerteam** möchten wir eine Projektstruktur im Repo (Quarkus-Module je Komponente), damit niemand im Code des anderen arbeitet. | Module `persistenz`, `worker`, `integration`, `eventing` · Build läuft | 2 | Saifudin | S1 |

## Epic E2 – Bestand und Versorgungsprofil (Persistenz)

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-03 | Als **Backoffice** möchte ich Versorgungsprofil (Produkt, Lieferant, Zielbestand, Mindestbestand, Preisgrenze) und Ist-Bestand dauerhaft speichern, damit der Prozess damit rechnen kann. | JPA-Entities `Versorgungsprofil`, `Bestand`, `Bestellung`, `Lieferung` · **Panache Repository-Stil** (kein `extends PanacheEntity`) · `@ApplicationScoped`, `@Inject`, `@Transactional` bei Änderungen | 5 | Erion | S1 |
| T2-04 | Als **Pflegeperson** möchte ich über die App einen abweichenden Bestand melden, damit die Versorgung stimmt. | REST `POST /bestand` (App-Simulation) speichert den Bestand · startet den Prozess über die Nachricht `PflegeApp_Bestandsmeldung_Team2` | 3 | Erion | S1 |
| T2-05 | Als **System** möchte ich bei Bestand < Mindestbestand automatisch einen Vorgang starten (bedingter Start). | Nach jeder Bestandsänderung `POST /condition` mit `bestandMenge`, `mindestbestand` · Instanz startet nur bei Unterschreitung | 3 | Erion | S2 |

## Epic E3 – Prozesslogik (Worker und Regeln)

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-06 | Als **Entwicklerteam** möchten wir alle 5 BPMN-Dateien auf CIB seven deployen, damit wir das Modell testen können. | Deploy ohne Fehler · Instanz startet im Cockpit | 2 | Saifudin | S1 |
| T2-07 | Als **Backoffice** möchte ich, dass Verbrauch und Reichweite berechnet werden und die Regel den Bedarf feststellt, damit rechtzeitig nachbestellt wird. | Worker `t2-reichweite-berechnen` · **DMN „Nachversorgungsbedarf“** setzt `nachversorgungErforderlich` · Worker `t2-vorgang-pruefen` (laufende Instanz mit Business Key `PH-<Haushalt>:<Produkt>` suchen, setzt `vorgangOffen`) | 5 | Saifudin | S1 |
| T2-08 | Als **Backoffice** möchte ich einen Bestellvorschlag (Menge = Zielbestand − Ist-Bestand, aufgerundet auf die Packung) und eine Ersatzprüfung, damit nur Abweichungen zum Menschen gehen und die Ersatz-Schleife endet. | Worker `t2-vorschlag-erstellen`, `t2-ersatzoption-pruefen` (setzt `ersatzMoeglich`, höchstens 2 Bestellversuche) · Abweichungen ermittelt die DMN „Berechtigungsregel“ | 5 | Saifudin | S2 |
| T2-09 | Als **Team 1, 2 und 3** möchten wir eine gemeinsame **Berechtigungsregel**, damit überall gleich entschieden wird, was ohne Freigabe erlaubt ist. | **DMN „Berechtigungsregel“** → `AUTOMATISCH` / `KUNDENFREIGABE` / `PRUEFUNG` · ermittelt die Abweichungen (Preis, Produktwechsel, Verbrauchssprung, Lieferant, Menge) · Quelle oder „Projektannahme“ je Regel | 5 | Saifudin | S2 |
| T2-10 | Als **Backoffice** möchte ich, dass nach der Lieferung der Bestand fortgeschrieben wird. | Worker `t2-bestand-fortschreiben` schreibt in die DB (nutzt Repository von T2-03) | 2 | Saifudin | S2 |

## Epic E4 – Pflege-App und Benachrichtigung (gemeinsame Funktion)

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-11 | Als **Pflegeperson** möchte ich Freigabeanfrage, Bestätigungsanfrage und jedes Ergebnis (auch Abbrüche mit Reichweitenrisiko) in der App sehen. | Ein Worker für die Sendeaufgaben und Nachrichten-Endereignisse (Topics `t2-freigabeanfrage-senden`, `t2-lieferbestaetigung-anfordern`, `t2-ergebnis-mitteilen`; schreibt bei Abbrüchen `vorgangszustand` fort) · schreibt die Nachricht in eine Tabelle/Log „App-Postfach“ (Simulation, klar gekennzeichnet) | 5 | **Saifudin** | S1 |
| T2-12 | Als **Pflegeperson** möchte ich in der App freigeben, ändern, ablehnen oder aufschieben und die Lieferung bestätigen. | REST-Endpunkte der App-Simulation → `POST /message` (`PflegeApp_Kundenentscheidung_Team2` mit FREIGEBEN/AENDERN/ABLEHNEN/AUFSCHIEBEN, `…_Lieferbestaetigung_Team2`) · Korrelation über `vorgangId` | 5 | Erion | S2 |
| T2-13 | Als **Team 1 und 3** möchten wir die Kundenentscheidung mitnutzen, damit wir keine eigene bauen müssen. | Schnittstellenvereinbarung (Vorlage D) mit Ein-/Ausgaben · im Integrationskreis vorgestellt · Entscheidung im Protokoll | 2 | **Saifudin** | S1 |

## Epic E5 – Bestellung und Lieferant (Messaging und Integration)

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-14 | Als **System** möchte ich die Bestellung asynchron in eine JMS-Queue senden. | Worker `t2-bestellung-senden` legt die Nachricht in die ActiveMQ-Queue · Queue-Namen in der README | 3 | Amar | S1 |
| T2-15 | Als **System** möchte ich die Bestellung mit Camel nach Inhalt an mehrere Ziele verteilen (CBR) und zwischen XML und JSON umwandeln. | Camel liest aus der Queue · CBR an mind. 2 Ziele (Datei/DB-Tabelle) · XML↔JSON in beide Richtungen | 8 | Amar | S1 |
| T2-16 | Als **Lieferant (simuliert)** möchte ich Bestellantwort und Versandmeldung schicken, damit der Prozess weiterläuft. | Postman/Datei → JMS → Camel → `POST /message` (`Lieferant_Bestellantwort_Team2`, `Lieferant_Versandmeldung_Team2`) · wartende Instanz läuft weiter | 5 | Amar | S2 |
| T2-17 | Als **Team 2** möchten wir Nachfass- und Klärungsauftrag an Team 3 senden und das Klärungsergebnis empfangen (vorerst simuliert). | Stub für Team 3 · Simulation erkennbar und austauschbar (Teamauftrag 7.1) | 5 | Amar | S2 |

## Epic E6 – Eventing (Esper)

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-18 | Als **Backoffice** möchte ich aus den Bestandsänderungen eine Verbrauchsprognose erkennen (z. B. Verbrauchssprung), damit keine stille Mengenerhöhung passiert. | Esper-Regel auf Bestandsereignisse · Ergebnis `verbrauchssprung` an den Prozess · Einsatz mit Stiehl abgestimmt (offen) | 5 | Amar | S2 |

## Epic E7 – Test, Doku, Integration

| ID | Story | Akzeptanzkriterien | Pkt | Wer | Sprint |
|---|---|---|---|---|---|
| T2-19 | Als **Entwicklerteam** möchten wir Testdaten (PH-0001 Bergmann, Testprodukt M) mit erwarteten Ergebnissen. | SQL-Skript für Testdaten · je Fall das erwartete Ende | 2 | **Saifudin** | S1 |
| T2-20 | Als **Prüfer** möchte ich eine Startanleitung, damit ich die Anwendung lokal starten kann. | Schritt für Schritt in der README · von einer anderen Person getestet | 2 | **Saifudin** | S2 |
| T2-21 | Als **Entwicklerteam** möchten wir den Happy Path Ende zu Ende vorführen (Meilenstein 2). | Timer-Start → Bestellung über JMS/Camel → Lieferant-Antwort → Lieferbestätigung → „Nachversorgung abgeschlossen“ · Protokoll (Vorlage G) | 3 | **alle** | S2 |
| T2-22 | Als **Team 2** möchten wir das BPMN aktuell halten, wenn sich bei der Umsetzung etwas ändert. | Jede Änderung mit Bild, Hinweis „Team 1/3 betroffen?“ und Entscheidung im Protokoll | 2 | **Saifudin** | S1–S2 |

## Sprint 3 (nach dem Meilenstein, noch nicht verteilt)

| ID | Story | Pkt |
|---|---|---|
| T2-23 | Ausnahmewege testen: Frist abgelaufen, Ablehnung, Änderung (max. 3), Teil-/Falschlieferung, Lieferant antwortet nicht | 8 |
| T2-24 | Probelauf mit Team 1 und 3 (Liefernachweis, Nachfassen, Kundenentscheidung) | 5 |
| T2-25 | Technische Fehler: Retries, Error-Boundary an Sendeaufgaben, doppelte Ereignisse erkennen | 5 |
| T2-26 | Pitch (15 Minuten): Problem, Lösung, Wow-Demo, Geschäftsmodell, Zukunft, je Person ein Teil | 5 |
| T2-27 | Abgabe: Code + Datenbankabzug an Stiehl, Fehlerliste, Lizenzhinweise | 2 |

## Saifudins Paket (das leichteste) in Kurzform
1. **T2-11 Benachrichtigungs-Worker:** ein External-Task-Worker, der die Topics für Anfragen und Ergebnis abholt und die Nachricht ins „App-Postfach“ schreibt. Wenig Logik, gut erklärbar.
2. **T2-13 Schnittstelle Kundenentscheidung:** Vorlage D ausfüllen, die Inhalte stehen schon in der README.
3. **T2-19 Testdaten:** ein SQL-Skript.
4. **T2-20 Startanleitung:** aufschreiben, was die anderen einrichten.
5. **T2-22 BPMN pflegen:** kennst du schon.
