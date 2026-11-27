# Team 2 – Aufgabenverteilung (Vorlage A „Teamrollen“)

> **Stand:** 27.11.2026 (Mohammeds Pakete T2-02, 06, 07, 08, 10 an Saifudin übergeben, weil bis dahin kein Commit dazu kam; DMN T2-09 ebenfalls an Saifudin, erste Fassung von Mohammed) · **Nächster Meilenstein:** 14.12.2026

## Warum so verteilt (Vorgaben von Stiehl)
- **Prüfungsamt:** Jedes Teammitglied verantwortet einen **eigenen, substanziellen Code-Anteil**. Der **gesamte Code** wird aufgeteilt. Wer welchen Code verantwortet, steht **als Kommentar im Code** (Projektvorgaben A).
- **Abnahme:** Jede Person muss **alle** Teile erklären können, auch die der anderen. Projekt und mündliche Abnahme zählen je etwa 50 %.
- **Pflicht-Technik:** BPMN, Persistenz (JPA/MySQL), Services (REST/SOAP, Quarkus), Messaging (ActiveMQ/JMS), Integration mit Transformation (Camel, CBR, XML↔JSON), Eventing (Esper). Gefordert ist ein **vertikaler Durchstich**.
- **Empfohlene Rollen** (Handbuch 9.1, Integrationspaket 3.3): Prozess und Fachlichkeit · Technische Umsetzung · Integration · Test und Dokumentation.
- **Team 2 stellt laut Teamauftrag 2.2 gemeinsame Funktionen für alle Teams bereit:** Kundenfreigabe, Benachrichtigung, Berechtigungsgrenzen.

## Bisher erledigt
| Person | Erledigt |
|---|---|
| Saifudin | Unterlagen gesammelt, Repo aufgebaut, komplettes BPMN-Modell (5 Dateien), Doku und Modell-Erklärung, Meilenstein-Vorstellung, Umbau nach Stiehls Feedback (3 Runden), Testdaten (#19), Schnittstelle Kundenentscheidung (#13), Benachrichtigungs-Worker (#11), **Mohammeds Pakete #2, #6, #7, #8, #10 übernommen** (PR #32), **DMN #9 übernommen** (27.11.) |
| Amar | Layout-Skript für die BPMN-Bilder, Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell |
| Erion | Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell |
| Mohammed | Abgleich der 11 Punkte aus Stiehls Rückmeldung mit dem überarbeiteten Modell, DMN „Nachversorgungsbedarf“ und „Berechtigungsregel“ mit DMN-Test (#9) |

**Folge (Stand 27.11.):** Saifudin trägt das größte Paket (34 Punkte), dann Amar (26) und Erion (16). Mohammed hat kein offenes Code-Paket mehr (ursprünglich 21 Punkte geplant).

## Verteilung
Die Aufgaben stehen als User Stories mit Akzeptanzkriterien, Punkten und Sprint im **[Backlog](Backlog.md)**.

| Person | Rolle | Code-Paket (eigener Anteil) | Stories | Punkte |
|---|---|---|---|---|
| **Amar** | Integration (Technik) | Messaging, Integration und Eventing: ActiveMQ, Camel (CBR, XML↔JSON), Lieferant-Simulation, Stubs für Team 3, **Esper** | T2-14 bis T2-18 | 26 |
| **Erion** | Technische Umsetzung | Persistenz (JPA/Panache Repository-Stil, MySQL), REST für die Pflege-App-Simulation, bedingter Start | T2-03, 04, 05, 12 | 16 |
| **Mohammed** | – | kein offenes Paket mehr (erste Fassung der DMN geliefert, T2-09 am 27.11. an Saifudin übergeben) | – | 0 |
| **Saifudin** | Prozess und Fachlichkeit, Integrationskreis, Prozesslogik | Benachrichtigungs-Worker, Schnittstelle Kundenentscheidung, Testdaten, Startanleitung, BPMN pflegen; **übernommen am 27.11.:** Projektstruktur, Worker der Prozesslogik, Deploy- und Endzustand-Test, DMN pflegen und testen (erste Fassung Mohammed) | T2-02, 06, 07, 08, 09, 10, 11, 13, 19, 20, 22 | 34 |

**Vertretungen:** Amar ↔ Erion (beide arbeiten an den Nachrichten zur Engine), Saifudin: Vertretung offen (im Team klären).

## Gemeinsame Aufgaben (alle)
- **Code-Kommentar** in jeder Datei: `// Verantwortlich: <Name>`.
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
