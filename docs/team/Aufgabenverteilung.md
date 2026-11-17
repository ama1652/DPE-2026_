# Team 2 – Aufgabenverteilung (Vorlage A „Teamrollen“)

> **KI-Kennzeichnung:** Vorschlag erstellt mit Claude (Anthropic) auf Basis von Projektvorgaben, Teamauftrag 2, Projekthandbuch (Kap. 9) und Integrationspaket (Kap. 3, Vorlagen A/B). Vom Team zu bestätigen.
>
> **Stand:** 17.11.2026 · **Nächster Meilenstein:** 14.12.2026 · Namen von Person C und D bitte eintragen.

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
| Amar | Layout-Skript für die BPMN-Bilder |
| Person C | – |
| Person D | – |

**Folge:** Bis zum 14.12. übernehmen **Amar, Person C und Person D die großen Code-Pakete**. Saifudin bekommt ein kleineres Code-Paket und pflegt das Modell.

## Verteilung

| Person | Rolle | Code-Paket (eigener Anteil) | Ergebnis bis 14.12.2026 |
|---|---|---|---|
| **Amar** | Integration (Technik) | **Messaging und Integration:** ActiveMQ-Queues; Camel-Route „Bestellung“ aus der JMS-Queue mit **CBR** an mindestens 2 Ziele (Datei/DB-Tabelle), **XML↔JSON**; **Lieferant-Simulation** (Postman/Datei → JMS → Camel → `POST /message` für `Lieferant_Bestellantwort_Team2` und `Lieferant_Versandmeldung_Team2`); Stubs für Team 3 (Nachfass- und Klärungsauftrag, Klärungsergebnis) | Bestellung läuft vom Prozess über JMS/Camel zum Lieferanten und die Antwort zurück in die wartende Instanz |
| **Person C** | Technische Umsetzung | **Persistenz und Services:** MySQL-Schema; JPA-Entities `Versorgungsprofil`, `Bestand`, `Bestellung`, `Lieferung` mit **Panache im Repository-Stil** (Stiehl: kein `extends PanacheEntity`), `@ApplicationScoped`; REST-API (Quarkus) für die **Pflege-App-Simulation**: Bestand melden, Kundenentscheidung, Kenntnisnahme, Lieferbestätigung → Nachricht an die Engine; Auslösen des bedingten Starts (`POST /condition`) nach jeder Bestandsänderung; Datenbankabzug | Bestand und Profile liegen in MySQL; die App-Simulation kann alle Antworten an den Prozess schicken |
| **Person D** | Prozesslogik + Test und Dokumentation | **External-Task-Worker und Regeln:** Worker (Quarkus) für die Service-Aufgaben (Reichweite berechnen, Vorschlag, Abweichungen prüfen, Bestand fortschreiben, Prüfung terminieren); **DMN** „Nachversorgungsbedarf“ und **„Berechtigungsregel“** (gemeinsame Funktion für alle Teams); Deploy-Test auf CIB seven; Testdaten (PH-0001 Bergmann, Testprodukt M); Startanleitung | Happy Path läuft in CIB seven von Start bis „Nachversorgung abgeschlossen“ (mit Simulationen) |
| **Saifudin** | Prozess und Fachlichkeit, Integrationskreis | **Eventing und Freigabe-Baustein:** **Esper**-Komponente (z. B. Verbrauchsprognose aus Bestandsänderungen oder doppelte Ereignisse erkennen, Einsatz mit Stiehl klären); **Benachrichtigungs-Worker** (Sendeaufgaben an die Pflege-App); Schnittstellenvereinbarung **Kundenentscheidung** mit Team 1 und 3 (Vorlage D); BPMN pflegen | Esper läuft mit einer Regel; Kundenentscheidung ist mit Team 1/3 abgestimmt |

**Vertretungen:** Amar ↔ Person C (beide arbeiten an den Nachrichten zur Engine), Person D ↔ Saifudin (Prozess und Worker).

## Gemeinsame Aufgaben (alle)
- **Code-Kommentar** in jeder Datei: `// Verantwortlich: <Name>`. Den KI-Anteil mit Beginn und Ende kennzeichnen und das Werkzeug nennen (z. B. „Claude“, „ChatGPT“).
- **Jede Person erklärt den anderen ihren Teil** (je 15 Minuten im Teamtermin). Alle lesen `prozesse/team2/MODELL_ERKLAERUNG.md` und können das Modell erklären.
- **Pitch** (15 Minuten, letzter Vorlesungstag), 1 Teil pro Person:
  - Problem: Saifudin
  - Lösung: Person C
  - Wow-Moment (Live-Demo): Amar + Person D
  - Geschäftsmodell und Zukunft: Person D
- **Wochenstatus** (Vorlage B): reihum. Wer dran ist, schreibt ihn nach dem Teamtermin ins Repo.

## Zeitplan bis zum Meilenstein 14.12.2026

| Woche | Amar | Person C | Person D | Saifudin |
|---|---|---|---|---|
| **bis 24.11.** | ActiveMQ + Camel aufsetzen, Queue-Namen festlegen | MySQL + Quarkus-Projekt, Entities und Repositories | CIB seven lokal, Deploy der 5 BPMN-Dateien, Worker-Grundgerüst | Schnittstelle Kundenentscheidung (Vorlage D) an Team 1/3; Esper-Einsatz mit Stiehl klären |
| **bis 01.12.** (Statusrunde Ende November) | Route Bestellung mit CBR + XML↔JSON | REST-Endpunkte der App-Simulation | Worker Bedarfsermittlung + DMN Nachversorgungsbedarf | Benachrichtigungs-Worker |
| **bis 08.12.** | Lieferant-Simulation → Engine | `POST /condition`, Testdaten in der DB | Worker Bestellfreigabe + DMN Berechtigungsregel | Esper-Regel läuft |
| **bis 14.12.** | Gemeinsamer Probelauf: **Happy Path Ende zu Ende** (alle) | | | |

Nach dem 14.12.: Ausnahmewege (Fristen, Ablehnung, Teillieferung), Probelauf mit Team 1 und 3, Pitch, Abgabe von Code und Datenbankabzug.

## Interne Arbeitsweise
| Punkt | Vereinbarung |
|---|---|
| Teamtermin | 1× pro Woche, 30 Minuten (Tag festlegen) |
| Aufgabenbrett | GitHub Issues im Repo, je Aufgabe eine verantwortliche Person |
| Entscheidungen | `docs/entscheidungen/README.md` (Vorlage C) |
| Integrationskreis | Saifudin (Vertretung: Person D) |
| Code-Änderungen | über Branch + Pull Request, eine zweite Person schaut drüber |
