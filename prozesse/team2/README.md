# Team 2 – Materialversorgung: BPMN-Modell

> **KI-Kennzeichnung (Kursregel):** Modelle, Bilder und dieser Text wurden mit KI-Unterstützung erstellt (Claude, Anthropic) und müssen von Team 2 geprüft werden. Wer im Team welchen Teil verantwortet, steht in [Aufgabenverteilung](../../docs/team/Aufgabenverteilung.md).
>
> **Stand:** 22.11.2026, **überarbeitet nach der schriftlichen Rückmeldung von Prof. Stiehl (11 Punkte)**, siehe [Runde 2](#runde-2-schriftliche-rückmeldung-von-stiehl-22112026). Davor: [Runde 1](#runde-1-feedback-beim-meilenstein-17112026) (Meilenstein). **Grundlage:** Teamauftrag 2, Gemeinsames Projekthandbuch, Integrations- und Organisationspaket (alle v1.0), Vorlesung „BPMN Best Practices“ (Method & Style). **Technik:** CIB seven (Camunda 7), External Tasks, JUEL. DMN siehe [DMN.md](DMN.md) (24.11.2026). Simulator und weitere Tests kommen später.

> **Ausführliche Erklärung, Schwächen und Prüfungsfragen:** [MODELL_ERKLAERUNG.md](MODELL_ERKLAERUNG.md)

## Überblick

| Datei | Inhalt | Teamauftrag-Schritte |
|---|---|---|
| `T2_Materialversorgung.bpmn` | **Hauptprozess:** 3 Starts, Prüfung auf offenen Vorgang, Bedarf (DMN) und Abschluss direkt im Fluss, 3 Call Activities, 8 Endzustände | 1–12 |
| `T2_Bestellfreigabe.bpmn` | Vorschlag, Berechtigungsregel (DMN), Kundenentscheidung oder Prüfstelle, 4 Ergebnisse | 4–7 |
| `T2_Kundenentscheidung.bpmn` | **Gemeinsamer Baustein** für Team 1, 2 und 3 (Senden/Empfangen über die Pflege-App, Nachfassen über Team 3) | 7 |
| `T2_Bestellabwicklung.bpmn` | Bestellung senden (JMS), Antwort empfangen, Nachfassen über Team 3, Ersatzoption prüfen | 8–9 |
| `T2_Lieferpruefung.bpmn` | Versand, Lieferbestätigung über die App, Klärung über Team 3 | 9–10 |
| `T2_Nachversorgungsbedarf.dmn` | Entscheidungstabelle: Reicht der Bestand bis Prüftermin + Lieferzeit? → [DMN.md](DMN.md) | 3 |
| `T2_Berechtigungsregel.dmn` | Entscheidungstabelle: AUTOMATISCH, KUNDENFREIGABE oder PRUEFUNG → [DMN.md](DMN.md) | 5–6 |

Eine Instanz entspricht einem Nachversorgungsvorgang für ein Produkt eines Pflegehaushalts, **Business Key `PH-<Haushalt>:<Produkt>`**. Den Ist-Bestand führt Team 2 selbst in der eigenen Datenbank (führendes System).

![Hauptprozess](bilder/T2_Materialversorgung.png)

## Runde 3: Besprechung mit Stiehl (25.11.2026)

Ergebnis: alle 11 Punkte besprochen, **grünes Licht** für das Deployment.

| Hinweis von Stiehl | Jetzt im Modell | Team 1/3 betroffen? |
|---|---|---|
| Ein eingebetteter Teilprozess lohnt sich nur bei Schleifenmarkierung, Boundary-Event oder komplexer Logik. | **Bedarfsermittlung** (2 Schritte) und **Vorgangsabschluss** (3 Schritte) liegen jetzt direkt im Hauptfluss. Die IDs der Schritte sind gleich geblieben. | Nein |
| Am verzweigenden XOR: ein Weg waagerecht, die anderen nach unten rechts bzw. oben rechts, Beschriftung auf dem waagerechten Teil. Keine zwei Flüsse aus einer Ecke. | Umgesetzt in Hauptprozess, Bestellfreigabe und Kundenentscheidung. Im Hauptprozess gehen die Abbruch-Enden treppenförmig nach oben rechts ab, damit sich nichts mit den Nachrichtenflüssen kreuzt. | Nein |
| Endereignisse am rechten Rand untereinander. | Umgesetzt in Bestellfreigabe, Kundenentscheidung, Bestellabwicklung und Lieferprüfung. Ausnahme: „Bestellung nicht zulässig“ bleibt in der Prüfstellen-Bahn (sonst Kreuzung mit der Schleife). | Nein |
| „Vorgang bereits offen“ ohne Nachricht an die App. | bleibt so (bestätigt) | Nein |
| DMN Hit Policy FIRST statt UNIQUE | bleibt FIRST, „wenn ihr euch der Konsequenzen bewusst seid“; AUTOMATISCH ist der Auffangfall | Nein |

## Runde 2: Schriftliche Rückmeldung von Stiehl (22.11.2026)

Stiehls Urteil: *„Die Modelle sind in sich weitgehend sauber.“* Was nicht passte, lag an den Übergängen zwischen den Ebenen und in der Fachlogik.

| Nr | Rückmeldung von Stiehl | Jetzt im Modell | Team 1/3 betroffen? |
|---|---|---|---|
| 1 | „Nächste Prüfung terminieren“ widerspricht dem festen Timer. | **Gestrichen.** Den nächsten Termin setzt allein der zyklische Timer „Prüftermin erreicht (alle 10 Tage)“. | Nein |
| 2 | Mehrere Instanzen gleichzeitig: ein zweiter Durchlauf kann doppelt bestellen. | Neu nach den Starts: Service-Aufgabe **„Laufenden Vorgang prüfen“** (sucht eine Instanz mit gleichem Business Key `PH-<Haushalt>:<Produkt>`) und Gateway **„Vorgang bereits offen?“** → Ende „Vorgang bereits offen“. | Nein |
| 3 | Abbruchpfade enden „stumm“: kein Ergebnis an die App, Reichweitenrisiko nur teilweise, Bestand nur im Erfolgsfall fortgeschrieben. | Jedes Ende ohne Lieferung ist ein **Nachrichten-Endereignis „Ergebnis“ an die Pflege-App** (External Task `t2-ergebnis-mitteilen`). Es meldet Ergebnis, Grund und Reichweitenrisiko und schreibt den Vorgang (Zustand, Grund) in der Datenbank fort. Den Bestand selbst ändert nur eine Lieferung, deshalb wird er nur im Abschluss fortgeschrieben. Die Quittung „Kenntnisnahme“ entfällt. | Nein (Pflege-App) |
| 4 | Fristen werden je Ebene anders eskaliert. | **Einheitlich:** Jede abgelaufene Frist (Kunde, Lieferant, Lieferung) geht an Team 3. In der Kundenentscheidung: Frist 3 Tage → „Nachfassen beauftragen“ (Team 3) → einmal erneut warten → sonst „Nicht freigegeben“. Die eigene Erinnerung und das Ende „Erinnerung gesendet“ sind gestrichen. | **Ja, Team 3** (Nachfassauftrag auch für Kundenentscheidungen). Nur Vorschlag. |
| 5 | In der Kundenentscheidung gehen Informationen verloren; „aufgeschoben“ ist keine Ablehnung. | Kundenentscheidung hat **4 Enden:** Freigegeben, Änderung gewünscht, **Aufgeschoben**, Nicht freigegeben. Bei „Nicht freigegeben“ steht in `kundenentscheidungGrund`, ob abgelehnt oder keine Antwort. Bestellfreigabe wertet alle 4 aus; „Aufgeschoben“ endet als eigenes Ergebnis „Bestellung aufgeschoben“. | **Ja, Team 1 und 3** (gemeinsamer Baustein, neues Ergebnis). Nur Vorschlag. |
| 6 | Prüfstelle: „zulässig, Freigabe ohne Kunde“ fehlt – bewusst? | **Bewusst nicht:** Jede Abweichung entscheidet der Kunde, die Prüfstelle kann nur „Kundenfreigabe einholen“ oder „nicht zulässig“. Entscheidung **T2-006**. | Nein |
| 7 | „Bestellung bestätigt?“ ist unvollständig, Ersatz-Schleife unbegrenzt, Grund wird nicht übergeben. | Nicht verfügbar oder keine Antwort trotz Nachfassen → **„Ersatzoption prüfen“** → „Ersatz erforderlich“ oder neues Ende **„Keine Bestellung möglich“**. Die Prüfung begrenzt die Schleife (`anzahlBestellversuche < 2`). Die Schleife übergibt `ersatzGrund` und `anzahlBestellversuche` an die Bestellfreigabe (Variablen-Mapping der Call Activity). | Nein |
| 8 | Die Entscheidung über Nachversorgung fällt zweimal. | Die Bedarfsermittlung hat **nur noch ein Ende „Bedarf ermittelt“** und liefert nur Daten. Das Gateway danach entscheidet auf `nachversorgungErforderlich`. | Nein |
| 9 | Mehrere Flüsse laufen ohne Gateway zusammen. | **Jede Zusammenführung über ein XOR-Merge** (vor „Produkt und Menge vorschlagen“, vor der Kundenentscheidung, vor der Bestellfreigabe, vor den Enden, vor „Klärungsfall übergeben“). Der Stilcheck prüft das jetzt automatisch. | Nein |
| 10 | Rollen passen nicht zusammen („Pflege-Backoffice“ vs. „Materialversorgung (Team 2)“). | **Einheitlich „Materialversorgung (Team 2)“** in allen Pools, Lanes „… – automatisiert“ und „… – menschliche Prüfstelle“. | Nein |
| 11 | Ergebnis von „Abweichungen prüfen“ wird nicht ausgewertet; Name „Erinnerung gesendet“ klingt fachlich. | „Abweichungen prüfen“ **gestrichen**: Die DMN „Berechtigungsregel“ ermittelt die Abweichungen und daraus den Freigabeweg. „Erinnerung gesendet“ gestrichen (siehe Punkt 4). | Nein |

**Abgleich (22.11.2026):** Erion, Mohammed und Amar sind die 11 Punkte von Stiehl durchgegangen und haben das überarbeitete Modell damit verglichen, ob jeder Punkt erfüllt ist.

## Runde 1: Feedback beim Meilenstein (17.11.2026)

Kernaussage von Stiehl: *Die Pflege-App ist ein eigenständiges System. Mit ihr arbeiten wir über Senden und Empfangen, nicht über Service-Aufgaben.*

| Nr | Feedback | Umgesetzt |
|---|---|---|
| 1 | Regelmäßiger Lauf = Timer-Ereignis | Zyklischer Timer-Start „Prüftermin erreicht (alle 10 Tage)“, eigener Prüflauf gelöscht |
| 2 | Bestand selbst führen → bedingter Start | Bedingter Start „Bestand unterschritten“, Pool Esper gelöscht |
| 3 | Bestand nicht nochmal abfragen | Bestandsabfrage gestrichen (T2-003) |
| 4 | Pflege-App = eigenständiges System | Senden-/Empfangen-Aufgaben statt Benutzeraufgaben |
| 5 | Mitteilungen sind Sendenachrichten | Alle Mitteilungen an die App als Senden |
| 6 | Quittung verlangen? | Damals Kenntnisnahme mit Nachfassen; in Runde 2 durch „Ergebnis“-Nachricht ersetzt |
| 7 | Happy Path: Empfangen mit angehängtem Timer | In Bestellabwicklung, Kundenentscheidung, Lieferprüfung |
| 8 | Wenige Schritte eingebettet und aufgeklappt | damals eingebettet; seit Runde 3 direkt im Fluss |

## Prozessgrenze
- **Start (3 Auslöser laut Teamauftrag):**
  - „Prüftermin erreicht (alle 10 Tage)“: zyklischer **Timer-Start** (`R/P10D`)
  - „Bestand manuell gemeldet“: **Nachrichtenstart** ← Pflege-App, Nachricht `PflegeApp_Bestandsmeldung_Team2`
  - „Bestand unterschritten“: **bedingter Start** auf den Bestand in der eigenen Datenbank. In CIB seven nach jeder Bestandsänderung per REST `POST /condition` auslösen.
- **Kein doppelter Vorgang:** „Laufenden Vorgang prüfen“ direkt nach den Starts.
- **Endzustände (Hauptprozess):**

| Endereignis | Art | Gemeinsamer Vorgangszustand (Handbuch 7.2) |
|---|---|---|
| Nachversorgung abgeschlossen | normal (Ergebnis wurde im Abschluss gesendet) | Erfolgreich abgeschlossen |
| Bestand ausreichend | normal | kein Vorgang nötig |
| Vorgang bereits offen | normal | – (der laufende Vorgang bleibt zuständig) |
| Bestellung nicht freigegeben | Nachricht „Ergebnis“ an die App | Erfolglos abgeschlossen (Grund: abgelehnt, keine Antwort oder keine Einigung) |
| Bestellung aufgeschoben | Nachricht „Ergebnis“ an die App | Erfolglos abgeschlossen (Reichweitenrisiko, nächster Prüftermin fragt erneut) |
| Bestellung nicht zulässig | Nachricht „Ergebnis“ an die App | Erfolglos abgeschlossen (Begründung der Prüfstelle) |
| Keine Bestellung möglich | Nachricht „Ergebnis“ an die App | Erfolglos abgeschlossen (kein Ersatz, Lieferant antwortet nicht) |
| Lieferung ungeklärt | Nachricht „Ergebnis“ an die App | Übergeben (an die menschliche Prüfstelle) |

Die Zuordnung zu den Zuständen ist ein Vorschlag für den Integrationskreis.

## Pflicht-Ausnahmen (Teamauftrag Abschnitt 5)

| Situation | Wo im Modell |
|---|---|
| Bestand nicht gemeldet | Entfällt: Den Bestand führt Team 2 selbst (T2-003). |
| Verbrauch deutlich verändert | Bedarfsermittlung markiert `verbrauchssprung` → Berechtigungsregel → Prüfstelle → Kundenfreigabe einholen oder nicht zulässig (keine stille Mengenerhöhung; siehe [DMN.md](DMN.md), offener Punkt 1) |
| Preisgrenze überschritten | Berechtigungsregel ermittelt die Abweichung → Kundenentscheidung |
| Bevorzugtes Produkt nicht verfügbar | Bestellabwicklung → „Ersatzoption prüfen“ → „Ersatz erforderlich“ (zurück zur Bestellfreigabe, nur hinterlegte Ersatzoptionen) oder „Keine Bestellung möglich“ |
| Lieferant antwortet nicht | Antwortfrist → Nachfassen über Team 3 → nach erneuter Frist „Ersatzoption prüfen“ |
| Teil- oder Falschlieferung | Lieferprüfung: „Abweichung festgestellt“ → Klärung über Team 3, Status bleibt offen |
| Kunde lehnt ab oder verschiebt | Kundenentscheidung „Nicht freigegeben“ bzw. „Aufgeschoben“ → Ende mit „Ergebnis“ an die App, Reichweitenrisiko sichtbar, keine Bestellung |
| *(Ergänzung)* Kunde wünscht immer wieder Änderungen | höchstens 3 Vorschläge, danach „Bestellung nicht freigegeben“ mit Grund „Keine Einigung“ |
| Lieferung bleibt unbestätigt | Bestätigungsfrist → Klärung, sonst „Lieferung ungeklärt“, nie automatisch erfolgreich |

## Umgesetzte Best Practices (Stiehl, Method & Style)
- **Führendes System entscheidet den Aufgabentyp:** Eigene Daten → Service- und Regelaufgaben. Fremde Systeme (Pflege-App, Lieferant, Team 1, Team 3) → Senden und Empfangen.
- **Top-down:** Hauptprozess mit höchstens 10 Aktivitäten. Große Teilprozesse als Call Activity (Call by Value); wenige Schritte direkt im Fluss (Runde 3).
- **Label-Matching (Regeln 10–12):** Endereignisse jedes Teilprozesses heißen genau wie die Ausgänge des folgenden Gateways. Jedes Endereignis setzt per Execution Listener `<teilprozess>Ergebnis = '<Name>'`.
- **Teilprozess-Enden steuern nicht, Daten steuern (Punkt 8, Regel 20):** Vor jedem Gateway liegt eine Aufgabe oder Regel, die das Ergebnis erzeugt.
- **Nachrichtenflüsse** in Eltern- und Kindebene gleich beschriftet (Regel 14), jede Sende-/Empfangsaufgabe hat einen Nachrichtenfluss (Regel 13), Partner sind Blackbox-Pools.
- **Happy Path sichtbar:** Empfangen-Aufgabe mit angehängtem Timer.
- **Einheitliche Eskalation:** Frist abgelaufen → einmal Nachfassen über Team 3 → dann Ergebnis. „Keine Antwort“ ist nie eine Freigabe.
- **Explizite Merges:** Jede Zusammenführung über ein XOR (Punkt 9).
- **Kein stummes Ende:** Jeder Abbruch meldet das Ergebnis per Nachrichten-Endereignis.

## Schnittstellen – nur Vorschlag, im Integrationskreis abstimmen

| Richtung | Nachricht / Funktion | Element |
|---|---|---|
| Pflege-App → Team 2 | `PflegeApp_Bestandsmeldung_Team2` (abweichender Ist-Bestand) | Nachrichtenstart |
| Team 2 → Pflege-App | Freigabe-Anfrage, Bestätigungs-Anfrage, **Ergebnis** (Erfolg und jeder Abbruch, inkl. Reichweitenrisiko) | Sendeaufgaben, Nachrichten-Endereignisse (`t2-ergebnis-mitteilen`) |
| Pflege-App → Team 2 | `PflegeApp_Kundenentscheidung_Team2` (`entscheidung` = FREIGEBEN, AENDERN, ABLEHNEN, AUFSCHIEBEN), `PflegeApp_Lieferbestaetigung_Team2` (`lieferbefund`) | Empfangen-Aufgaben |
| Team 2 → Lieferant (simuliert) | Bestellung (JMS) | `t2-bestellung-senden` |
| Lieferant → Team 2 | `Lieferant_Bestellantwort_Team2`, `Lieferant_Versandmeldung_Team2` | Empfangen-Aufgaben |
| Team 2 → Team 3 | Nachfass-Auftrag (Kunde oder Lieferant antwortet nicht) | `t2-nachfassen-beauftragen` |
| Team 2 → Team 3 | Klärungs-Auftrag (Abweichung, Gegenstelle) | `t2-klaerung-beauftragen` |
| Team 3 → Team 2 | `Team3_Klaerungsergebnis_Team2` (`NACHLIEFERUNG_BESTAETIGT` oder `NICHT_GEKLAERT`) | Empfangen-Aufgabe |
| Team 2 → Team 1 | Liefernachweis | `t2-nachweis-uebergeben` |
| Team 2 → Team 1/3 | **Kundenentscheidung** als Call Activity `T2_Kundenentscheidung` (Ein: `freigabeHandlung`, `freigabeBegruendung`, `freigabeFolgen`, `freigabeGueltigBis`; Aus: `kundenentscheidungErgebnis` = Freigegeben, Änderung gewünscht, Aufgeschoben, Nicht freigegeben; `kundenentscheidungGrund`) | eigener Prozess |

Jede teamübergreifende Nachricht soll den gemeinsamen Ereignisrahmen tragen (Integrationspaket 6.5): `ereignisId`, `ereignistyp`, `zeitpunkt`, `quelle`, `pflegehaushaltId`, `vorgangId`, `korrelationsId`, `schemaVersion`, `nutzdaten`.

## Projektannahmen – nicht von Stiehl vorgegeben
- Fristen: Antwortfrist Kunde 3 Tage, Antwortfrist Lieferant 1 Tag, Versandfrist 5 Tage, Bestätigungsfrist 3 Tage, Klärungsfrist 7 Tage; jeweils einmal Nachfassen über Team 3, wo modelliert. Prüftermin alle 10 Tage (Beispiel von Stiehl). Später konfigurierbar (DMN „Fristen“).
- Höchstens 3 Vorschläge je Bestellfreigabe, höchstens 2 Bestellversuche (Ersatz).

## Offen (Stiehl/Integrationskreis)
- **Timer-Start und Instanz:** Ein Timer-Start erzeugt je Zyklus eine Instanz ohne Haushalt und Produkt. Wie werden die fälligen Versorgungsprofile zugeordnet? (Frage für den Termin am 25.11.)
- **Esper:** Eventing ist Pflicht. Wo setzen wir Esper ein, z. B. für die Verbrauchsprognose?
- Gemeinsame Kennungen (`PH-…`, `VG-T2-…`) und Nachrichtenformate
- Wie Team 1 und 3 die Kundenentscheidung aufrufen (Call Activity oder Nachricht), und ob Team 3 Nachfassaufträge für Kundenentscheidungen übernimmt
- Wer betreibt die Pflege-App, und wer ist Empfänger von „Klärungsfall übergeben“?

## Prüfung (22.11.2026)
- XSD-Prüfung gegen das offizielle BPMN-2.0-Schema: 5/5 gültig
- bpmnlint (recommended): 0 Fehler (nur Hinweise „Element is unused“ für Nachrichten, die über `messageRef` genutzt werden)
- Eigener Stilcheck (`werkzeuge/stilcheck.py`): Label-Matching, Nachrichtenflüsse Eltern/Kind, höchstens 10 Aktivitäten, höchstens 2 eingehende Linien, **jede Zusammenführung über XOR (neu, Punkt 9)**, Camunda-Pflichtattribute → keine Fehler
- Logikprüfung: Jeder Schritt ist erreichbar, jeder Weg führt zu einem Ende
- **Noch nicht gemacht:** Deploy auf einer laufenden CIB-seven-Engine. Bitte lokal prüfen:

```bash
cd prozesse/team2
curl -s -X POST http://localhost:8080/engine-rest/deployment/create \
  -F deployment-name=team2-bpmn -F enable-duplicate-filtering=true \
  $(for f in *.bpmn; do echo -n "-F $f=@$f "; done)
```
