# Schnittstellenvereinbarung: Kundenentscheidung (Vorlage D)

> **KI-Kennzeichnung (Kursregel):** Entwurf erstellt mit Claude (Anthropic) auf Basis von Integrationspaket (Vorlage D, Kap. 6.2–7.5), Teamauftrag 2 (Kap. 2.2) und unserem Modell `prozesse/team2/T2_Kundenentscheidung.bpmn`. Verantwortlich im Team: Saifudin Mohammadi (Story T2-13).
>
> **Status:** **Entwurf – Vorschlag zur Abstimmung im Integrationskreis.** Nicht einseitig festgelegt. Team 1 und Team 3 müssen zustimmen, bevor sie die Schnittstelle nutzen.

## Kopf

| Feld | Eintrag |
|---|---|
| Name und Version | `T2_Kundenentscheidung` · Version **1.0 (Entwurf)** · Stand 24.11.2026 |
| Bereitstellendes Team | Team 2 – Materialversorgung (Teamauftrag 2.2: Team 2 verantwortet die gemeinsamen Funktionen für Kundenfreigaben, Benachrichtigungen und Berechtigungsgrenzen) |
| Nutzende Teams | Team 2 (Bestellfreigabe) · **Team 1** – Verwaltung und Erstattung · **Team 3** – Geplante Abwesenheit *(Nutzung durch Team 1/3: offen, Integrationskreis)* |
| Fachlicher Zweck | Eine ausdrückliche Entscheidung der Pflegeperson zu einer geplanten Handlung einholen (z. B. Bestellung mit Mehrkosten, Ersatzprodukt, Einreichung, Gesamtplan). Keine Antwort ist **nie** eine Freigabe. |
| Auslöser | Ein Prozess braucht eine Kundenfreigabe, weil eine Berechtigungsgrenze überschritten ist (DMN „Berechtigungsregel“ → `KUNDENFREIGABE`) oder die Prüfstelle sie verlangt. |
| Vorbedingungen | Pflegehaushalt und Vorgang existieren (`pflegehaushaltId`, `vorgangId`) · Handlung, Begründung und Folgen sind beschrieben · die Pflegeperson ist über die Pflege-App erreichbar |
| Erwartetes Ergebnis | Genau eines von 4 Ergebnissen in `kundenentscheidungErgebnis`: **Freigegeben**, **Änderung gewünscht**, **Aufgeschoben**, **Nicht freigegeben** (Grund in `kundenentscheidungGrund`) |
| Simulierter Dienst, Ort und Startanleitung | **Pflege-App-Simulation** (Story T2-12, Erion): REST-Endpunkt, der die Antwort als Nachricht `PflegeApp_Kundenentscheidung_Team2` an die Engine schickt (`POST /engine-rest/message`). Bis dahin per Postman/curl, siehe [Testaufruf](#testaufruf-simulation). Die Simulation ist sichtbar gekennzeichnet (Integrationspaket 7.5). |

## Ablauf (kurz)

1. **Freigabeanfrage senden** an die Pflege-App (External Task `t2-freigabeanfrage-senden`).
2. **Kundenentscheidung empfangen** (Empfangsaufgabe, Nachricht `PflegeApp_Kundenentscheidung_Team2`).
3. Keine Antwort nach **3 Tagen** → einmal **Nachfassen über Team 3** (`t2-nachfassen-beauftragen`) → erneut 3 Tage warten → sonst „Nicht freigegeben“ (Grund: keine Antwort).

Die Frist von 3 Tagen ist eine **Projektannahme** (nicht von Stiehl vorgegeben).

## Aufruf

| Variante | Wie | Für wen |
|---|---|---|
| A – Call Activity (empfohlen) | `<bpmn:callActivity calledElement="T2_Kundenentscheidung">` mit `camunda:in`/`camunda:out` wie unten | Teams in derselben CIB-seven-Engine |
| B – Nachricht | Start per Nachricht, Ergebnis per Nachricht zurück | nur falls getrennte Engines *(offen, Integrationskreis)* |

## Eingaben

| Feld | Typ | Pflicht | Bedeutung | Beispiel |
|---|---|---|---|---|
| `pflegehaushaltId` | String | ja | Gemeinsamer Pflegehaushalt (Integrationspaket 6.2) | `PH-0001` |
| `vorgangId` | String | ja | Vorgang des aufrufenden Teams, dient auch zur Korrelation der Antwort | `VG-T2-0001` |
| `freigabeHandlung` | String | ja | Was soll freigegeben werden? | `Bestellung 3 × Testprodukt M à 27,50 € = 82,50 €` |
| `freigabeBegruendung` | String | ja | Warum ist eine Freigabe nötig? | `Gesamtpreis 82,50 € über der Freigabegrenze von 75,00 €` |
| `freigabeFolgen` | String | ja | Was passiert bei Ablehnung oder Aufschub? | `Bestand reicht noch ca. 7 Tage (Reichweitenrisiko)` |
| `freigabeGueltigBis` | Datum (ISO 8601) | nein | Bis wann gilt das Angebot? | `2026-12-01` |

## Antwort der Pflege-App (Nachricht an die Engine)

| Feld | Typ | Pflicht | Werte |
|---|---|---|---|
| `messageName` | String | ja | `PflegeApp_Kundenentscheidung_Team2` |
| `processVariables.entscheidung` | String | ja | `FREIGEBEN` · `AENDERN` · `ABLEHNEN` · `AUFSCHIEBEN` |
| `processVariables.kommentar` | String | nein | Freitext der Pflegeperson |
| Korrelation | – | ja | über `vorgangId` bzw. Business Key der wartenden Instanz |

## Ergebnis und Fehler

| Fall | Antwort (`kundenentscheidungErgebnis` / `…Grund`) | Wiederholung | Nächste Handlung beim Aufrufer |
|---|---|---|---|
| Pflegeperson gibt frei | `Freigegeben` | – | Handlung ausführen |
| Pflegeperson wünscht Änderung | `Änderung gewünscht` | ja, mit neuem Vorschlag | neuen Vorschlag machen (Team 2: höchstens 3, dann „Keine Einigung“) |
| Pflegeperson schiebt auf | `Aufgeschoben` · Grund `Kunde: aufgeschoben` | beim nächsten Anlass (z. B. Prüftermin) | Handlung nicht ausführen, Risiko sichtbar machen, **keine Ablehnung** |
| Pflegeperson lehnt ab | `Nicht freigegeben` · Grund `Kunde: abgelehnt` | nein | Handlung nicht ausführen, Ergebnis mitteilen |
| Keine Antwort trotz Nachfassen | `Nicht freigegeben` · Grund `Kunde: keine Antwort trotz Nachfassen` | nein | wie Ablehnung, Grund dokumentieren |
| Pflichtangabe fehlt beim Aufruf | Fehlerantwort nach Integrationspaket 7.3, z. B. `fehlercode: PFLICHTFELD_FEHLT`, `betroffenes Feld: freigabeHandlung` | ja, nach Ergänzung | Eingaben ergänzen und erneut aufrufen *(technische Umsetzung offen)* |
| Pflege-App nicht erreichbar | External Task wird wiederholt (Retries), danach Incident im Cockpit | ja, automatisch | Betrieb prüfen *(Error-Boundary: Story T2-25)* |

## Abhängigkeiten

| Von | Was | Status |
|---|---|---|
| Team 3 | nimmt den **Nachfass-Auftrag** an (Kundenentscheidung ohne Antwort) | offen, Integrationskreis (Entscheidung T2-009) |
| Pflege-App | zeigt Anfrage, sendet Antwort mit Korrelation | Simulation durch Team 2 (T2-12) |

## Änderungsregel

| Kompatible Änderung | Nicht kompatible Änderung | Übergang |
|---|---|---|
| neues **optionales** Eingabefeld, neuer Text in `…Grund`, längere Frist | neues Pflichtfeld, neuer oder umbenannter Ergebniswert, geänderter Nachrichtenname | nur nach Beschluss im Integrationskreis (Vorlage C), neue Version 2.0, alte Version bleibt bis zur vereinbarten Frist deploybar (`calledElementBinding="version"`) |

## Testaufruf (Simulation)

Antwort der Pflegeperson simulieren, solange die App-Simulation (T2-12) fehlt:

```bash
curl -s -X POST http://localhost:8080/engine-rest/message \
  -H "Content-Type: application/json" \
  -d '{
        "messageName": "PflegeApp_Kundenentscheidung_Team2",
        "businessKey": "PH-0001:TP-M",
        "processVariables": {
          "entscheidung": { "value": "FREIGEBEN", "type": "String" }
        }
      }'
```

Testfälle mit erwartetem Ergebnis: TF04–TF08 in [testdaten/team2](../../testdaten/team2/README.md).

## Ansprechpartner
Saifudin Mohammadi (Integrationskreis Team 2), Vertretung: Mohammed.
