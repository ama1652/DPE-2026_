# Team 2 – Aufgabenverteilung (Vorlage A „Teamrollen“)

> **KI-Kennzeichnung:** Vorschlag erstellt mit Claude (Anthropic) auf Basis von Projektvorgaben, Teamauftrag 2, Projekthandbuch (Kap. 9) und Integrationspaket (Kap. 3, Vorlagen A/B). Vom Team zu bestätigen.
>
> **Stand:** 22.11.2026 · **Nächster Meilenstein:** 14.12.2026

## Warum so verteilt (Vorgaben von Stiehl)
- **Prüfungsamt:** Jedes Teammitglied verantwortet einen **eigenen, substanziellen Code-Anteil**. Der **gesamte Code** wird aufgeteilt. Wer welchen Code verantwortet, steht **als Kommentar im Code** (Projektvorgaben A).
- **Abnahme:** Jede Person muss **alle** Teile erklären können, auch die der anderen. Projekt und mündliche Abnahme zählen je etwa 50 %.
- **Pflicht-Technik:** BPMN, Persistenz (JPA/MySQL), Services (REST/SOAP, Quarkus), Messaging (ActiveMQ/JMS), Integration mit Transformation (Camel, CBR, XML↔JSON), Eventing (Esper). Gefordert ist ein **vertikaler Durchstich**.
- **Empfohlene Rollen** (Handbuch 9.1, Integrationspaket 3.3): Prozess und Fachlichkeit · Technische Umsetzung · Integration · Test und Dokumentation.
- **Team 2 stellt laut Teamauftrag 2.2 gemeinsame Funktionen für alle Teams bereit:** Kundenfreigabe, Benachrichtigung, Berechtigungsgrenzen.

## Bisher erledigt
| Person | Erledigt |
|---|---|
| Saifudin | Unterlagen gesammelt, Repo aufgebaut, komplettes BPMN-Modell (5 Dateien), Doku und Modell-Erklärung, Meilenstein-Vorstellung, Umbau nach Stiehls Feedback |
| Amar | Layout-Skript für die BPMN-Bilder, Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell |
| Erion | Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell |
| Mohammed | Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell |

**Folge:** Bis zum 14.12. übernehmen **Amar und Mohammed die beiden schwersten Pakete**, danach Erion. Reihenfolge nach Schwierigkeit: Amar (26 Punkte), Mohammed (21), Erion (16), Saifudin (13, kleinstes Paket).

## Verteilung
Die Aufgaben stehen als User Stories mit Akzeptanzkriterien, Punkten und Sprint im **[Backlog](Backlog.md)**.

| Person | Rolle | Code-Paket (eigener Anteil) | Stories | Punkte |
|---|---|---|---|---|
| **Amar** | Integration (Technik) | Messaging, Integration und Eventing: ActiveMQ, Camel (CBR, XML↔JSON), Lieferant-Simulation, Stubs für Team 3, **Esper** | T2-14 bis T2-18 | 26 |
| **Erion** | Technische Umsetzung | Persistenz (JPA/Panache Repository-Stil, MySQL), REST für die Pflege-App-Simulation, bedingter Start | T2-03, 04, 05, 12 | 16 |
| **Mohammed** | Prozesslogik | External-Task-Worker, DMN „Nachversorgungsbedarf“ und „Berechtigungsregel“, Deploy auf CIB seven, Projektstruktur | T2-02, 06, 07, 08, 09, 10 | 21 |
| **Saifudin** | Prozess und Fachlichkeit, Integrationskreis | Benachrichtigungs-Worker, Schnittstelle Kundenentscheidung, Testdaten, Startanleitung, BPMN pflegen | T2-11, 13, 19, 20, 22 | 13 |

**Vertretungen:** Amar ↔ Erion (beide arbeiten an den Nachrichten zur Engine), Mohammed ↔ Saifudin (Prozess und Worker).

## Gemeinsame Aufgaben (alle)
- **Code-Kommentar** in jeder Datei: `// Verantwortlich: <Name>`. Den KI-Anteil mit Beginn und Ende kennzeichnen und das Werkzeug nennen (z. B. „Claude“, „ChatGPT“).
- **Jede Person erklärt den anderen ihren Teil** (je 15 Minuten im Teamtermin). Alle lesen `prozesse/team2/MODELL_ERKLAERUNG.md` und können das Modell erklären.
- **Pitch** (15 Minuten, letzter Vorlesungstag), 1 Teil pro Person:
  - Problem: Saifudin
  - Lösung: Erion
  - Wow-Moment (Live-Demo): Amar + Mohammed
  - Geschäftsmodell und Zukunft: Mohammed
- **Wochenstatus** (Vorlage B): reihum. Wer dran ist, schreibt ihn nach dem Teamtermin ins Repo.

## Zeitplan
Sprint 1 (17.11.–30.11.) und Sprint 2 (01.12.–14.12., Meilenstein 2: Happy Path Ende zu Ende) stehen mit allen Stories im [Backlog](Backlog.md). Sprint 3 bis zur Abgabe: Ausnahmewege, Probelauf mit Team 1/3, Pitch, Abgabe von Code und Datenbankabzug.

## Interne Arbeitsweise
| Punkt | Vereinbarung |
|---|---|
| Teamtermin | 1× pro Woche, 30 Minuten (Tag festlegen) |
| Aufgabenbrett | [GitHub Issues #1–#27](https://github.com/mohammadisaifuddin187-dev/DPE-2026_/issues) (Nummer = Story-ID), Filter über Labels `wer: …` und Meilensteine `Sprint 1–3` |
| Entscheidungen | `docs/entscheidungen/README.md` (Vorlage C) |
| Integrationskreis | Saifudin (Vertretung: Mohammed) |
| Code-Änderungen | über Branch + Pull Request, eine zweite Person schaut drüber |
