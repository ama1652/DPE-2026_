# Team 2 – Testdaten (Story T2-19)

> Verantwortlich im Team: Saifudin Mohammadi. Grundlage: Integrationspaket Kap. 8.1 (künstlicher Testhaushalt). Alle Namen und Werte sind frei erfunden. Zahlen sind **Projektannahmen**, nicht von Prof. Stiehl vorgegeben.

## Inhalt
- [`T2_Testdaten.sql`](T2_Testdaten.sql): Stammdaten (Haushalt, Lieferant, Produkte, Versorgungsprofil, Ausgangsbestand) und 16 Testfälle mit erwartetem Ende (Tabelle `t2_testfall`)
- Tabellen- und Spaltennamen sind ein **Vorschlag**. **Erion (T2-03)** gleicht sie mit seinen JPA-Entities ab. Legt Hibernate das Schema an, nur Teil 2 und 3 ausführen.

```bash
mysql -u <user> -p <datenbank> < testdaten/team2/T2_Testdaten.sql
```

## Stammdaten

| Gegenstand | Wert |
|---|---|
| Pflegehaushalt | `PH-0001` Haushalt Bergmann (Erika Bergmann, Pflegegrad 2; Hauptpflegeperson Anna Bergmann) |
| Lieferant | `LF-0001` Versorgungsdienst Beispiel, Lieferzeit 3 Tage *(Annahme)* |
| Produkt | `TP-M` Testprodukt M, Inkontinenzmaterial, 30 Stück je Packung, 24,90 € *(Annahme)* |
| Ersatzoption | `TP-M-PLUS` Testprodukt M Plus, 26,40 € *(hinterlegt, kein medizinischer Ersatz)* |
| Versorgungsprofil | Zielbestand 120 · Mindestbestand 40 · Verbrauch 4 Stück/Tag · Preisgrenze 75,00 € je Bestellung · Prüfung alle 10 Tage |
| Business Key | `PH-0001:TP-M` |

**Rechenregel (Annahme für die DMN „Nachversorgungsbedarf“):** nachbestellen, wenn Reichweite = Ist-Bestand ÷ Verbrauch < 10 + 3 = 13 Tage. Bestellmenge = Zielbestand − Ist-Bestand, aufgerundet auf volle Packung. Den Freigabeweg bestimmt Mohammeds DMN „Berechtigungsregel“ ([DMN.md](../../prozesse/team2/DMN.md)): Produkt nicht hinterlegt oder Verbrauchssprung → Prüfstelle; Gesamtpreis > 75 €, Ersatzprodukt, anderer Lieferant oder Menge > Zielbestand → Kundenfreigabe; sonst automatisch.

## Testfälle – jeder Endzustand des Hauptprozesses kommt vor

| Fall | Situation | Simulation | Erwartetes Ende | Vorgangszustand |
|---|---|---|---|---|
| TF01 | Happy Path (30 Stück, Preis unter Grenze) | Lieferant bestätigt, Lieferung richtig | Nachversorgung abgeschlossen | Erfolgreich abgeschlossen |
| TF02 | Bestand reicht (110 Stück = 27,5 Tage) | – | Bestand ausreichend | – |
| TF03 | Zweiter Start während TF01 läuft | manuelle Bestandsmeldung | Vorgang bereits offen | – |
| TF04 | Preis über Grenze (3 × 27,50 € = 82,50 €) | Kunde: FREIGEBEN | Nachversorgung abgeschlossen | Erfolgreich abgeschlossen |
| TF05 | Preis über Grenze | Kunde: ABLEHNEN | Bestellung nicht freigegeben | Erfolglos abgeschlossen |
| TF06 | Preis über Grenze | Kunde: AUFSCHIEBEN | Bestellung aufgeschoben | Erfolglos abgeschlossen |
| TF07 | Preis über Grenze | keine Antwort, Nachfassen Team 3, wieder keine | Bestellung nicht freigegeben | Erfolglos abgeschlossen |
| TF08 | Preis über Grenze | Kunde: 3× AENDERN | Bestellung nicht freigegeben | Erfolglos abgeschlossen |
| TF09 | Produkt nicht im Profil hinterlegt | Prüfstelle: NICHT_ZULAESSIG | Bestellung nicht zulässig | Erfolglos abgeschlossen |
| TF10 | Verbrauch 4 → 12 Stück/Tag | Prüfstelle: Kundenfreigabe einholen, Kunde: FREIGEBEN | Nachversorgung abgeschlossen | Erfolgreich abgeschlossen |
| TF11 | Produkt nicht verfügbar, Ersatz hinterlegt | Ersatz freigegeben, 2. Versuch bestätigt | Nachversorgung abgeschlossen | Erfolgreich abgeschlossen |
| TF12 | Produkt nicht verfügbar, kein Ersatz | – | Keine Bestellung möglich | Erfolglos abgeschlossen |
| TF13 | Lieferant antwortet nicht, kein Ersatz | Nachfassen Team 3, wieder keine Antwort | Keine Bestellung möglich | Erfolglos abgeschlossen |
| TF14 | Teillieferung | Team 3: NACHLIEFERUNG_BESTAETIGT | Nachversorgung abgeschlossen | Erfolgreich abgeschlossen |
| TF15 | Falschlieferung | Team 3: NICHT_GEKLAERT | Lieferung ungeklärt | Übergeben |
| TF16 | Lieferung bleibt unbestätigt | keine Bestätigung, keine Klärung | Lieferung ungeklärt | Übergeben |

Damit sind alle 8 Endzustände des Hauptprozesses und alle Pflicht-Ausnahmen aus Teamauftrag Abschnitt 5 abgedeckt. Die Fälle sind auch die Grundlage für den Deploy-Test (T2-06) und die Ausnahmetests (T2-23).

Die Testfälle laufen **nacheinander**, weil alle denselben Business Key haben (TF03 prüft genau das). Vor jedem Fall den Bestand in `t2_bestand` auf `ist_bestand` setzen.
