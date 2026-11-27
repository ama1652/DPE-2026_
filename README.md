# DPE-2026 – Pflege-Backoffice MVP, Team 2 Materialversorgung

Semesterprojekt im Modul **Digital Process Engineering** (Prof. Dr. Volker Stiehl, THI, WS 2026/27).
Team 2 baut den Prozess **„Verbrauchsmaterial rechtzeitig nachversorgen“** und die gemeinsamen Funktionen
für Kundenfreigaben, Benachrichtigungen und Berechtigungsgrenzen.

**Lizenz:** Selbst erstellte Bestandteile stehen unter der [MIT-Lizenz](LICENSE).
**Ausgenommen** ist der Ordner `unterlagen/`. Er enthält Dokumente von Prof. Stiehl, die nicht unter MIT stehen, und muss vor einer öffentlichen Freigabe des Repos entfernt werden.


## Struktur
| Pfad | Inhalt |
|---|---|
| `prozesse/team2/` | BPMN- und DMN-Modelle (CIB seven / Camunda 7), Bilder, Erläuterung → [README](prozesse/team2/README.md) |
| `docs/schnittstellen/` | Schnittstellenvorschläge für den Integrationskreis |
| `docs/entscheidungen/` | Entscheidungsprotokoll |
| `docs/team/` | Aufgabenverteilung und Rollen im Team → [Aufgabenverteilung](docs/team/Aufgabenverteilung.md) |
| `werkzeuge/` | Prüfskript für Stilregeln und Label-Matching, Engine-Test für die DMN (`dmn-test/`) |
| `unterlagen/` | Kickoff-Unterlagen und Projektvorgaben von Prof. Stiehl (nicht MIT) |

## Stand
- [x] BPMN: Hauptprozess (3 Starts, 2 eingebettete Teilprozesse) und 4 Call-Activity-Teilprozesse (inkl. gemeinsamer Baustein Kundenentscheidung), überarbeitet nach dem Feedback von Prof. Stiehl → [Erklärung, Schwächen, offene Fragen](prozesse/team2/MODELL_ERKLAERUNG.md)
- [x] DMN „Nachversorgungsbedarf“ und „Berechtigungsregel“ (Entwurf, von der Engine per `decisionRef` aufgerufen, getestet) → [DMN.md](prozesse/team2/DMN.md)
- [ ] DMN „Fristen“
- [ ] External-Task-Worker, Camel-Routen (JMS, CBR), simulierter Lieferant
- [ ] Tests und teamübergreifender Beispieldurchlauf
