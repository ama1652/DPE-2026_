"""Erzeugt die BPMN-Modelle von Team 2 (Materialversorgung) für CIB seven.
fachlich abzustimmen und zu prüfen durch Team 2.
Stand nach der schriftlichen Rückmeldung von Prof. Stiehl (Mail, 22.11.2026, Punkte 1-11).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bpmnbuilder import Process, Collab, build

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'prozesse', 'team2')
os.makedirs(OUT, exist_ok=True)
HDR = ''

# Einheitliche Benennung (Stiehl Punkt 10): alles von Team 2 heißt "Materialversorgung (Team 2)"
T2 = 'Materialversorgung (Team 2)'
LIEFERANT = 'Lieferant (simuliert)'
TEAM3 = 'Team 3 - Kommunikation, Fristen, Nachfassen'
TEAM1 = 'Team 1 - Verwaltung und Erstattung'
APP = 'Pflege-App'
PA = 'Projektannahme (nicht von Stiehl vorgegeben, im Integrationskreis bestätigen): '

# Nachrichtenflüsse: gleiche Namen in Eltern- und Kindmodell (Regel 14)
N_ANFRAGE = 'Freigabe-Anfrage'
N_ENTSCHEIDUNG = 'Kunden-Entscheidung'
N_NACHFASS = 'Nachfass-Auftrag'
N_BESTELLUNG = 'Bestellung'
N_BANTWORT = 'Bestell-Antwort'
N_VERSAND = 'Versand-Meldung'
N_BANFRAGE = 'Bestätigungs-Anfrage'
N_LBEST = 'Liefer-Bestätigung'
N_KAUFTRAG = 'Klärungs-Auftrag'
N_KERGEBNIS = 'Klärungs-Ergebnis'
N_ERGEBNIS = 'Ergebnis'


def ergebnis(var, wert):
    return f"${{execution.setVariable('{var}', '{wert}')}}"


def setze(var, wert):
    return f"${{execution.setVariable('{var}', '{wert}')}}"


# ---------------------------------------------------------------- Hauptprozess
def hauptprozess():
    p = Process('T2_Materialversorgung', 'Materialversorgung',
                doc='Hauptprozess Team 2: Verbrauchsprodukte rechtzeitig und kontrolliert nachversorgen (Teamauftrag 2). '
                    'Eine Instanz = ein Nachversorgungsvorgang für ein Produkt eines Pflegehaushalts '
                    '(Business Key PH-<Haushalt>:<Produkt>). Den Ist-Bestand führt Team 2 in der eigenen Datenbank. '
                    'Jedes Ende ohne Lieferung meldet Ergebnis und Reichweitenrisiko an die Pflege-App (Stiehl Punkt 3). '
                    'Nach der Besprechung am 25.11.: keine eingebetteten Teilprozesse mehr (Bedarfsermittlung und '
                    'Vorgangsabschluss liegen direkt im Fluss), Verzweigungen waagerecht plus oben rechts.')
    Y = 520
    abbruch = ('Sendendes Nachrichten-Endereignis: meldet Ergebnis und Reichweitenrisiko an die Pflege-App '
               'und schreibt den Vorgang (Zustand, Grund) in der Datenbank fort (Stiehl Punkt 3).')
    erfolglos = [setze('vorgangszustand', 'Erfolglos abgeschlossen')]
    # --- drei Starts
    p.add('Start_Timer', 'startEvent', 'Prüftermin erreicht (alle 10 Tage)', 200, Y + 150, ev='timer',
          timer=('timeCycle', 'R/P10D'), label_w=100,
          doc='Zyklischer Timer-Start. Er ersetzt jedes eigene Terminieren (Stiehl Punkt 1). '
              'Offen (Stiehl): Zuordnung der fälligen Haushalte/Produkte zu den Instanzen.')
    p.add('Start_Manuell', 'startEvent', 'Bestand manuell gemeldet', 260, Y, ev='message', message='Msg_Bestandsmeldung',
          label_w=90, integration=True, doc='Die Pflegeperson meldet über die Pflege-App einen abweichenden Ist-Bestand.')
    p.add('Start_Bedingt', 'startEvent', 'Bestand unterschritten', 350, Y - 130, label='top', label_w=90,
          ev='conditional', condition='${bestandMenge < mindestbestand}',
          doc='Bedingter Start auf den Bestand der eigenen Datenbank. CIB seven: nach jeder Bestandsänderung '
              'REST "POST /condition" (die Engine überwacht keine Tabellen).')
    p.add('GW_Start', 'exclusiveGateway', '', 350, Y,
          listeners=["${execution.setVariable('anzahlBestellversuche', 0)}"])
    # --- Punkt 2: läuft schon ein Vorgang?
    p.add('T_Offen', 'serviceTask', 'Laufenden Vorgang prüfen', 470, Y, topic='t2-vorgang-pruefen',
          doc='Sucht eine laufende Instanz mit gleichem Business Key PH-<Haushalt>:<Produkt> (Stiehl Punkt 2). '
              'Ergebnis vorgangOffen (true/false). So kann kein zweiter Durchlauf doppelt bestellen.')
    p.add('GW_Offen', 'exclusiveGateway', 'Vorgang bereits offen?', 590, Y, label='bottom', label_w=80)
    p.add('End_Offen', 'endEvent', 'Vorgang bereits offen', 700, Y - 90, label='bottom', label_w=80,
          doc='Kein zweiter Vorgang; der laufende Vorgang arbeitet mit dem aktuellen Bestand aus der Datenbank. '
              'Bewusst ohne Nachricht an die App (Besprechung mit Prof. Stiehl, 25.11.2026).')
    # --- Bedarf: direkt im Fluss (Besprechung 25.11.: kein Teilprozess für zwei Schritte)
    p.add('SB_Reichweite', 'serviceTask', 'Verbrauch und Reichweite berechnen', 790, Y, topic='t2-reichweite-berechnen',
          doc='Liest Ist-Bestand, Verbrauchsannahme, Mindest- und Zielbestand aus der eigenen Datenbank und setzt die '
              'Eingaben der DMN: istBestand, verbrauchProTag, tageBisPruefung, lieferzeitTage, mindestbestand, '
              'zielbestand; dazu verbrauchssprung bei deutlich verändertem Verbrauch.')
    p.add('SB_Bedarf', 'businessRuleTask', 'Nachversorgungsbedarf feststellen', 950, Y, size=(150, 80),
          decision='Nachversorgungsbedarf', result='bedarfErgebnis',
          doc='DMN "Nachversorgungsbedarf" (T2_Nachversorgungsbedarf.dmn, Verantwortlich: Mohammed): Reicht der Bestand '
              'bis zum nächsten Prüftermin plus Lieferzeit? Die Engine wertet die Tabelle selbst aus (decisionRef). '
              'Ausgaben: nachversorgungErforderlich, nachversorgungsbedarf, bedarfsbegruendung.',
          listeners=[("${execution.setVariable('nachversorgungErforderlich', bedarfErgebnis.nachversorgungErforderlich)}", 'end'),
                     ("${execution.setVariable('nachversorgungsbedarf', bedarfErgebnis.nachversorgungsbedarf)}", 'end'),
                     ("${execution.setVariable('bedarfsbegruendung', bedarfErgebnis.bedarfsbegruendung)}", 'end')])
    p.add('GW_Bedarf', 'exclusiveGateway', 'Nachversorgung erforderlich?', 1070, Y, label=(990, 563, 76), label_w=76,
          doc='Entscheidet auf den Daten der DMN (nachversorgungErforderlich), Stiehl Punkt 8.')
    p.add('End_Ausreichend', 'endEvent', 'Bestand ausreichend', 1160, Y + 90, label='bottom', label_w=80,
          doc='Kein Handlungsbedarf; der nächste zyklische Timer prüft erneut.')
    p.add('XOR_BF', 'exclusiveGateway', '', 1250, Y)
    p.add('CA_Bestellfreigabe', 'callActivity', 'Bestellfreigabe', 1450, Y, size=(320, 80), called='T2_Bestellfreigabe',
          ins=['pflegehaushaltId', 'vorgangId', 'produktId', 'nachversorgungsbedarf', 'verbrauchssprung', 'ersatzGrund',
               'anzahlBestellversuche'],
          outs=['bestellfreigabeErgebnis', 'bestellvorschlag', 'ablehnungsgrund'])
    p.add('GW_Freigabe', 'exclusiveGateway', 'Bestellung freigegeben?', 1690, Y, label=(1610, 563, 76), label_w=76)
    # Abbruch-Enden oben rechts, Treppe von unten-rechts nach oben-links (keine Kreuzung mit Nachrichtenflüssen)
    p.add('End_NichtFreigegeben', 'endEvent', 'Bestellung nicht freigegeben', 2000, Y - 90, ev='message',
          topic='t2-ergebnis-mitteilen', label='bottom', label_w=90, integration=True, doc=abbruch, listeners=erfolglos)
    p.add('End_Aufgeschoben', 'endEvent', 'Bestellung aufgeschoben', 1910, Y - 180, ev='message',
          topic='t2-ergebnis-mitteilen', label='bottom', label_w=80, integration=True,
          doc=abbruch + ' Aufgeschoben ist keine Ablehnung: Reichweitenrisiko sichtbar machen (Teamauftrag 2, '
                        'Abschnitt 5); der nächste Prüftermin fragt erneut.', listeners=erfolglos)
    p.add('End_NichtZulaessig', 'endEvent', 'Bestellung nicht zulässig', 1820, Y - 270, ev='message',
          topic='t2-ergebnis-mitteilen', label='bottom', label_w=80, integration=True, doc=abbruch, listeners=erfolglos)
    p.add('CA_Bestellabwicklung', 'callActivity', 'Bestellabwicklung', 2240, Y, size=(320, 80), called='T2_Bestellabwicklung',
          ins=['pflegehaushaltId', 'vorgangId', 'bestellvorschlag', 'anzahlBestellversuche'],
          outs=['bestellabwicklungErgebnis', 'bestellung', 'ersatzGrund'],
          listeners=["${execution.setVariable('anzahlBestellversuche', anzahlBestellversuche + 1)}"])
    p.add('GW_Bestellung', 'exclusiveGateway', 'Bestellung bestätigt?', 2480, Y, label=(2400, 563, 76), label_w=76)
    p.add('End_KeineBestellung', 'endEvent', 'Keine Bestellung möglich', 2600, Y - 90, ev='message',
          topic='t2-ergebnis-mitteilen', label='bottom', label_w=80, integration=True, doc=abbruch, listeners=erfolglos)
    p.add('CA_Lieferpruefung', 'callActivity', 'Lieferprüfung', 2990, Y, size=(560, 80), called='T2_Lieferpruefung',
          ins=['pflegehaushaltId', 'vorgangId', 'bestellung'], outs=['lieferpruefungErgebnis', 'lieferung'])
    p.add('GW_Lieferung', 'exclusiveGateway', 'Lieferung abgeschlossen?', 3340, Y, label=(3260, 563, 76), label_w=76)
    p.add('End_Ungeklaert', 'endEvent', 'Lieferung ungeklärt', 3460, Y - 90, ev='message', topic='t2-ergebnis-mitteilen',
          label='bottom', label_w=70, integration=True,
          doc=abbruch + ' Der Fall ist an die menschliche Prüfstelle übergeben.',
          listeners=[setze('vorgangszustand', 'Übergeben')])
    # --- Abschluss: direkt im Fluss (Besprechung 25.11.: kein Teilprozess für drei Schritte)
    p.add('SA_Fortschreiben', 'serviceTask', 'Bestand und Verbrauch fortschreiben', 3600, Y, topic='t2-bestand-fortschreiben',
          doc='Neuer Ist-Bestand und neue Reichweite in der eigenen Datenbank.')
    p.add('SA_Nachweis', 'sendTask', 'Liefernachweis übergeben', 3770, Y, topic='t2-nachweis-uebergeben', integration=True,
          doc='An Team 1. Schnittstelle = Vorschlag zur Abstimmung.')
    p.add('SA_Ergebnis', 'sendTask', 'Ergebnis mitteilen', 3940, Y, topic='t2-ergebnis-mitteilen', integration=True,
          doc='Nachricht an die Pflege-App: Lieferung abgeschlossen, neuer Bestand.')
    p.add('End_Abgeschlossen', 'endEvent', 'Nachversorgung abgeschlossen', 4080, Y, label_w=90,
          listeners=[setze('vorgangszustand', 'Erfolgreich abgeschlossen')])

    # --- Sequenzflüsse (Verzweigung: ein Weg waagerecht, die anderen über oben/unten rechts)
    p.flow('F01', 'Start_Manuell', 'GW_Start')
    p.flow('F02', 'Start_Bedingt', 'GW_Start', 'bottom', 'top')
    p.flow('F03', 'Start_Timer', 'GW_Start', 'right', 'bottom')
    p.flow('F04', 'GW_Start', 'T_Offen')
    p.flow('F05', 'T_Offen', 'GW_Offen')
    p.flow('F06', 'GW_Offen', 'End_Offen', 'top', 'left', via=[(590, Y - 90)], name='Ja', cond='${vorgangOffen}',
           label=(600, Y - 112, 30))
    p.flow('F07', 'GW_Offen', 'SB_Reichweite', name='Nein', cond='${!vorgangOffen}', label=(616, Y - 22, 34))
    p.flow('F08', 'SB_Reichweite', 'SB_Bedarf')
    p.flow('F09', 'SB_Bedarf', 'GW_Bedarf')
    p.flow('F10', 'GW_Bedarf', 'XOR_BF', name='Ja', cond='${nachversorgungErforderlich}', label=(1100, Y - 20, 30))
    p.flow('F11', 'GW_Bedarf', 'End_Ausreichend', 'bottom', 'left', via=[(1070, Y + 90)], name='Nein',
           cond='${!nachversorgungErforderlich}', label=(1080, Y + 68, 34))
    p.flow('F12', 'XOR_BF', 'CA_Bestellfreigabe')
    p.flow('F13', 'CA_Bestellfreigabe', 'GW_Freigabe')
    p.flow('F14', 'GW_Freigabe', 'CA_Bestellabwicklung', name='Bestellung freigegeben',
           cond="${bestellfreigabeErgebnis == 'Bestellung freigegeben'}", label=(1730, Y - 34, 90))
    p.flow('F15', 'GW_Freigabe', 'End_NichtFreigegeben', 'top', 'left', via=[(1690, Y - 90)],
           name='Bestellung nicht freigegeben', cond="${bestellfreigabeErgebnis == 'Bestellung nicht freigegeben'}",
           label=(1700, Y - 122, 90))
    p.flow('F16', 'GW_Freigabe', 'End_Aufgeschoben', 'top', 'left', via=[(1690, Y - 180)],
           name='Bestellung aufgeschoben', cond="${bestellfreigabeErgebnis == 'Bestellung aufgeschoben'}",
           label=(1700, Y - 212, 90))
    p.flow('F17', 'GW_Freigabe', 'End_NichtZulaessig', 'top', 'left', via=[(1690, Y - 270)],
           name='Bestellung nicht zulässig', cond="${bestellfreigabeErgebnis == 'Bestellung nicht zulässig'}",
           label=(1700, Y - 302, 90))
    p.flow('F18', 'CA_Bestellabwicklung', 'GW_Bestellung')
    p.flow('F19', 'GW_Bestellung', 'CA_Lieferpruefung', name='Bestellung bestätigt',
           cond="${bestellabwicklungErgebnis == 'Bestellung bestätigt'}", label=(2515, Y - 34, 80))
    p.flow('F20', 'GW_Bestellung', 'End_KeineBestellung', 'top', 'left', via=[(2480, Y - 90)],
           name='Keine Bestellung möglich', cond="${bestellabwicklungErgebnis == 'Keine Bestellung möglich'}",
           label=(2490, Y - 122, 90))
    p.flow('F21', 'GW_Bestellung', 'XOR_BF', 'bottom', 'bottom', via=[(2480, Y + 150), (1250, Y + 150)],
           name='Ersatz erforderlich', cond="${bestellabwicklungErgebnis == 'Ersatz erforderlich'}",
           label=(2380, Y + 122, 90))
    p.flow('F22', 'CA_Lieferpruefung', 'GW_Lieferung')
    p.flow('F23', 'GW_Lieferung', 'SA_Fortschreiben', name='Lieferung abgeschlossen',
           cond="${lieferpruefungErgebnis == 'Lieferung abgeschlossen'}", label=(3372, Y - 34, 80))
    p.flow('F24', 'GW_Lieferung', 'End_Ungeklaert', 'top', 'left', via=[(3340, Y - 90)], name='Lieferung ungeklärt',
           cond="${lieferpruefungErgebnis == 'Lieferung ungeklärt'}", label=(3350, Y - 122, 90))
    p.flow('F25', 'SA_Fortschreiben', 'SA_Nachweis')
    p.flow('F26', 'SA_Nachweis', 'SA_Ergebnis')
    p.flow('F27', 'SA_Ergebnis', 'End_Abgeschlossen')

    W = 4080
    c = Collab('Collab_T2_Materialversorgung')
    c.participant('P_Team3', TEAM3, 120, 10, W, 50)
    c.participant('P_Lieferant', LIEFERANT, 120, 70, W, 50)
    c.participant('P_PflegeApp', APP, 120, 130, W, 50)
    c.participant('P_Materialversorgung', T2, 120, 200, W, 560, process=p.id)
    c.participant('P_Team1', TEAM1, 120, 800, W, 60)
    bf, ba, lp = 'CA_Bestellfreigabe', 'CA_Bestellabwicklung', 'CA_Lieferpruefung'
    LY = 215

    def lab(x):
        return (x + 4, LY, 110)
    c.msg('M01', 'Bestandsmeldung', 'P_PflegeApp', 'Start_Manuell', [(260, 180), (260, 502)], (200, 420, 70))
    c.msg('M02', N_ANFRAGE, bf, 'P_PflegeApp', [(1330, 480), (1330, 180)], lab(1330))
    c.msg('M03', N_ENTSCHEIDUNG, 'P_PflegeApp', bf, [(1450, 180), (1450, 480)], lab(1450))
    c.msg('M04', N_NACHFASS, bf, 'P_Team3', [(1570, 480), (1570, 60)], lab(1570))
    c.msg('M05', N_ERGEBNIS, 'End_NichtZulaessig', 'P_PflegeApp', [(1820, 232), (1820, 180)], (1824, 196, 48))
    c.msg('M06', N_ERGEBNIS, 'End_Aufgeschoben', 'P_PflegeApp', [(1910, 322), (1910, 180)], (1914, 196, 48))
    c.msg('M07', N_ERGEBNIS, 'End_NichtFreigegeben', 'P_PflegeApp', [(2000, 412), (2000, 180)], (2004, 196, 48))
    c.msg('M08', N_BESTELLUNG, ba, 'P_Lieferant', [(2120, 480), (2120, 120)], lab(2120))
    c.msg('M09', N_BANTWORT, 'P_Lieferant', ba, [(2240, 120), (2240, 480)], lab(2240))
    c.msg('M10', N_NACHFASS, ba, 'P_Team3', [(2360, 480), (2360, 60)], lab(2360))
    c.msg('M11', N_ERGEBNIS, 'End_KeineBestellung', 'P_PflegeApp', [(2600, 412), (2600, 180)], (2604, 196, 48))
    c.msg('M12', N_VERSAND, 'P_Lieferant', lp, [(2750, 120), (2750, 480)], lab(2750))
    c.msg('M13', N_BANFRAGE, lp, 'P_PflegeApp', [(2870, 480), (2870, 180)], lab(2870))
    c.msg('M14', N_LBEST, 'P_PflegeApp', lp, [(2990, 180), (2990, 480)], lab(2990))
    c.msg('M15', N_KAUFTRAG, lp, 'P_Team3', [(3110, 480), (3110, 60)], lab(3110))
    c.msg('M16', N_KERGEBNIS, 'P_Team3', lp, [(3230, 60), (3230, 480)], lab(3230))
    c.msg('M17', N_ERGEBNIS, 'End_Ungeklaert', 'P_PflegeApp', [(3460, 412), (3460, 180)], (3464, 196, 48))
    c.msg('M18', 'Liefernachweis', 'SA_Nachweis', 'P_Team1', [(3770, 560), (3770, 800)], (3774, 770, 80))
    c.msg('M19', N_ERGEBNIS, 'SA_Ergebnis', 'P_PflegeApp', [(3940, 480), (3940, 180)], (3944, LY, 48))
    build(f'{OUT}/T2_Materialversorgung.bpmn', c, [p],
          [('Msg_Bestandsmeldung', 'PflegeApp_Bestandsmeldung_Team2')], HDR)


# ---------------------------------------------------------------- Bestellfreigabe
def bestellfreigabe():
    p = Process('T2_Bestellfreigabe', 'Bestellfreigabe',
                doc='Teilprozess zu Schritt 4-7. Eine Abweichung führt nicht zur Ablehnung, sondern zu einer menschlichen '
                    'Entscheidung (Kunde oder Prüfstelle). Die Prüfstelle kann bewusst nicht ohne Kunde freigeben '
                    '(Entscheidung T2-006, Stiehl Punkt 6). Ergebnis bestellfreigabeErgebnis, Grund in ablehnungsgrund.')
    Y = 340
    p.add('Start', 'startEvent', 'Bestellvorschlag angefordert', 190, Y, label_w=90,
          listeners=["${execution.setVariable('anzahlVorschlaege', 0)}"])
    p.add('XOR_V', 'exclusiveGateway', '', 280, Y)
    p.add('T_Vorschlag', 'serviceTask', 'Produkt und Menge vorschlagen', 400, Y, topic='t2-vorschlag-erstellen',
          doc='Bevorzugtes Produkt aus dem Versorgungsprofil; Menge = Zielbestand minus Ist-Bestand, aufgerundet auf die '
              'Packung. Bei ersatzGrund oder Änderungswunsch nur hinterlegte Ersatzoptionen. Zählt anzahlVorschlaege.',
          listeners=[("${execution.setVariable('anzahlVorschlaege', anzahlVorschlaege + 1)}", 'end')])
    p.add('T_Regel', 'businessRuleTask', 'Berechtigungsregel anwenden', 580, Y,
          decision='Berechtigungsregel', result='berechtigungErgebnis',
          doc='DMN "Berechtigungsregel" (T2_Berechtigungsregel.dmn, Verantwortlich: Mohammed): ermittelt die Abweichungen '
              '(Preis, Produktwechsel, Verbrauchssprung, Lieferant, Menge) und daraus freigabeweg = AUTOMATISCH, '
              'KUNDENFREIGABE oder PRUEFUNG. Ersetzt "Abweichungen prüfen" (Stiehl Punkt 11). Die Engine wertet die '
              'Tabelle selbst aus (decisionRef). Hit Policy FIRST, mit Prof. Stiehl am 25.11. besprochen.',
          listeners=[("${execution.setVariable('freigabeweg', berechtigungErgebnis.freigabeweg)}", 'end'),
                     ("${execution.setVariable('freigabeBegruendung', berechtigungErgebnis.freigabeBegruendung)}", 'end')])
    p.add('GW_Weg', 'exclusiveGateway', 'Freigabeweg?', 720, Y, label=(650, 292, 66), label_w=66)
    p.add('XOR_KE', 'exclusiveGateway', '', 880, Y)
    p.add('CA_KE', 'callActivity', 'Kundenentscheidung', 1060, Y, size=(260, 80), called='T2_Kundenentscheidung',
          ins=['pflegehaushaltId', 'vorgangId', 'freigabeHandlung', 'freigabeBegruendung', 'freigabeFolgen', 'freigabeGueltigBis'],
          outs=['kundenentscheidungErgebnis', 'kundenentscheidungGrund'],
          doc='Gemeinsamer Baustein Kundenentscheidung (auch für Team 1 und Team 3).')
    p.add('GW_KE', 'exclusiveGateway', 'Entscheidung?', 1250, Y, label=(1196, 284, 72), label_w=72)
    p.add('XOR_Frei', 'exclusiveGateway', '', 1430, Y)
    p.add('End_Freigegeben', 'endEvent', 'Bestellung freigegeben', 1560, Y, label='right', label_w=90,
          listeners=[ergebnis('bestellfreigabeErgebnis', 'Bestellung freigegeben')])
    p.add('End_Aufgeschoben', 'endEvent', 'Bestellung aufgeschoben', 1560, 410, label='right', label_w=90,
          listeners=[ergebnis('bestellfreigabeErgebnis', 'Bestellung aufgeschoben')])
    p.add('XOR_N', 'exclusiveGateway', '', 1430, 480)
    p.add('End_NichtFreigegeben', 'endEvent', 'Bestellung nicht freigegeben', 1560, 480, label='right', label_w=90,
          listeners=[ergebnis('bestellfreigabeErgebnis', 'Bestellung nicht freigegeben')])
    p.add('GW_Weiter', 'exclusiveGateway', 'Weiterer Vorschlag möglich?', 1370, 560, label=(1390, 590, 90), label_w=90)
    p.add('UT_Grenzfall', 'userTask', 'Grenzfall prüfen', 720, 740, group='pruefstelle',
          form=[('freigabeBegruendung', 'Anlass der Prüfung', 'string', {'readonly': True}),
                ('pruefergebnis', 'Prüfergebnis', 'enum', {'required': True, 'values': [
                    ('KUNDENFREIGABE', 'Kundenfreigabe einholen'), ('NICHT_ZULAESSIG', 'Nicht zulässig')]}),
                ('pruefbegruendung', 'Begründung', 'string', {'required': True})],
          doc='Anlass: ungewöhnlicher Verbrauch, ungeklärtes Produkt oder Grenzfall. Rolle: menschliche Prüfstelle '
              '(Mitarbeitende von Team 2, Tasklist). Ergebnis: Kundenfreigabe einholen oder nicht zulässig. '
              'Ein "zulässig ohne Kunde" gibt es bewusst nicht: jede Abweichung entscheidet der Kunde (T2-006).')
    p.add('GW_Pruef', 'exclusiveGateway', 'Prüfergebnis?', 880, 740, label='bottom', label_w=70)
    p.add('End_NichtZulaessig', 'endEvent', 'Bestellung nicht zulässig', 990, 740, label='right', label_w=80,
          listeners=[ergebnis('bestellfreigabeErgebnis', 'Bestellung nicht zulässig'),
                     setze('ablehnungsgrund', 'Prüfstelle: nicht zulässig')])

    p.flow('F01', 'Start', 'XOR_V')
    p.flow('F02', 'XOR_V', 'T_Vorschlag')
    p.flow('F03', 'T_Vorschlag', 'T_Regel')
    p.flow('F04', 'T_Regel', 'GW_Weg')
    p.flow('F05', 'GW_Weg', 'XOR_KE', name='Kundenfreigabe erforderlich', cond="${freigabeweg == 'KUNDENFREIGABE'}",
           label=(750, 306, 100))
    p.flow('F06', 'GW_Weg', 'XOR_Frei', 'top', 'top', via=[(720, 210), (1430, 210)], name='Automatisch zulässig',
           cond="${freigabeweg == 'AUTOMATISCH'}", label=(730, 184, 120))
    p.flow('F07', 'GW_Weg', 'UT_Grenzfall', 'bottom', 'top', name='Prüfung erforderlich', cond="${freigabeweg == 'PRUEFUNG'}",
           label=(728, 560, 70))
    p.flow('F08', 'UT_Grenzfall', 'GW_Pruef')
    p.flow('F09', 'GW_Pruef', 'XOR_KE', 'top', 'bottom', name='Kundenfreigabe einholen',
           cond="${pruefergebnis == 'KUNDENFREIGABE'}", label=(886, 560, 70))
    p.flow('F10', 'GW_Pruef', 'End_NichtZulaessig', name='Nicht zulässig', cond="${pruefergebnis == 'NICHT_ZULAESSIG'}",
           label=(896, 712, 76))
    p.flow('F11', 'XOR_KE', 'CA_KE')
    p.flow('F12', 'CA_KE', 'GW_KE')
    p.flow('F13', 'GW_KE', 'XOR_Frei', name='Freigegeben', cond="${kundenentscheidungErgebnis == 'Freigegeben'}",
           label=(1300, Y - 22, 80))
    p.flow('F14', 'GW_KE', 'End_Aufgeschoben', 'bottom', 'left', via=[(1250, 410)], name='Aufgeschoben',
           cond="${kundenentscheidungErgebnis == 'Aufgeschoben'}", label=(1262, 388, 80),
           listeners=[setze('ablehnungsgrund', 'Kunde: aufgeschoben')])
    p.flow('F15', 'GW_KE', 'XOR_N', 'bottom', 'left', via=[(1250, 480)], name='Nicht freigegeben',
           cond="${kundenentscheidungErgebnis == 'Nicht freigegeben'}", label=(1262, 458, 110),
           listeners=["${execution.setVariable('ablehnungsgrund', kundenentscheidungGrund)}"])
    p.flow('F16', 'GW_KE', 'GW_Weiter', 'bottom', 'left', via=[(1250, 560)], name='Änderung gewünscht',
           cond="${kundenentscheidungErgebnis == 'Änderung gewünscht'}", label=(1258, 530, 60))
    p.flow('F17', 'GW_Weiter', 'XOR_V', 'bottom', 'bottom', via=[(1370, 850), (280, 850)], name='Ja',
           cond='${anzahlVorschlaege < 3}', label=(1376, 800, 30))
    p.flow('F18', 'GW_Weiter', 'XOR_N', 'right', 'bottom', via=[(1430, 560)], name='Nein (keine Einigung)',
           cond='${anzahlVorschlaege >= 3}', label=(1436, 515, 110),
           listeners=[setze('ablehnungsgrund', 'Keine Einigung nach 3 Vorschlägen')])
    p.flow('F19', 'XOR_Frei', 'End_Freigegeben')
    p.flow('F20', 'XOR_N', 'End_NichtFreigegeben')
    W = 1680
    p.lanes = [('Lane_System', T2 + ' - automatisiert',
                ['Start', 'XOR_V', 'T_Vorschlag', 'T_Regel', 'GW_Weg', 'XOR_KE', 'CA_KE', 'GW_KE', 'XOR_Frei',
                 'End_Freigegeben', 'End_Aufgeschoben', 'GW_Weiter', 'XOR_N', 'End_NichtFreigegeben'], 90, 160, W - 30, 460),
               ('Lane_Pruefstelle', T2 + ' - menschliche Prüfstelle', ['UT_Grenzfall', 'GW_Pruef', 'End_NichtZulaessig'],
                90, 620, W - 30, 260)]
    c = Collab('Collab_T2_Bestellfreigabe')
    c.participant('P_Team3', TEAM3, 60, 10, W, 50)
    c.participant('P_PflegeApp', APP, 60, 70, W, 50)
    c.participant('P_Bestellfreigabe', 'Bestellfreigabe - ' + T2, 60, 160, W, 720, process=p.id)
    c.msg('M01', N_ANFRAGE, 'CA_KE', 'P_PflegeApp', [(970, 300), (970, 120)], (872, 252, 92))
    c.msg('M02', N_ENTSCHEIDUNG, 'P_PflegeApp', 'CA_KE', [(1060, 120), (1060, 300)], (1064, 252, 80))
    c.msg('M03', N_NACHFASS, 'CA_KE', 'P_Team3', [(1150, 300), (1150, 60)], (1154, 252, 92))
    build(f'{OUT}/T2_Bestellfreigabe.bpmn', c, [p], [], HDR)


# ---------------------------------------------------------------- Kundenentscheidung (gemeinsamer Baustein)
def kundenentscheidung():
    p = Process('T2_Kundenentscheidung', 'Kundenentscheidung',
                doc='Gemeinsamer Baustein (Team 2 verantwortet Kundenfreigaben, Handbuch 6.2 / 7.4). Die Pflege-App ist ein '
                    'eigenständiges System: Anfrage senden, Entscheidung empfangen. Ablauf der Frist: wie überall Nachfassen '
                    'über Team 3, danach einmal erneut warten (Stiehl Punkt 4). Ergebnis kundenentscheidungErgebnis: '
                    'Freigegeben | Änderung gewünscht | Aufgeschoben | Nicht freigegeben; bei "Nicht freigegeben" sagt '
                    'kundenentscheidungGrund, ob abgelehnt oder keine Antwort (Stiehl Punkt 5). Keine Antwort ist nie eine Freigabe.')
    Y = 300
    p.add('Start', 'startEvent', 'Entscheidung angefordert', 170, Y, label_w=90,
          listeners=["${execution.setVariable('nachgefasst', false)}"])
    p.add('S_Anfrage', 'sendTask', 'Freigabeanfrage senden', 300, Y, topic='t2-freigabeanfrage-senden', integration=True,
          doc='Nachricht an die Pflege-App mit Handlung, Begründung, Folgen und Gültigkeit.')
    p.add('XOR_W', 'exclusiveGateway', '', 430, Y)
    p.add('R_Entscheidung', 'receiveTask', 'Kundenentscheidung empfangen', 560, Y, message='Msg_Kundenentscheidung',
          integration=True, doc='Antwort aus der Pflege-App, Variable entscheidung: FREIGEBEN, AENDERN, ABLEHNEN, AUFSCHIEBEN.')
    p.add('B_Frist', 'boundaryEvent', 'Antwortfrist abgelaufen (3 Tage)', 560, 340, attached='R_Entscheidung', ev='timer',
          timer=('timeDuration', 'P3D'), label=(456, 350, 96), label_w=96, doc=PA + 'Antwortfrist 3 Tage.')
    p.add('GW_Nach', 'exclusiveGateway', 'Bereits nachgefasst?', 560, 440, label=(456, 452, 90), label_w=90)
    p.add('S_Nachfassen', 'sendTask', 'Nachfassen beauftragen', 560, 540, topic='t2-nachfassen-beauftragen', integration=True,
          doc='Team 3 fasst bei der Pflegeperson nach. Schnittstelle = Vorschlag zur Abstimmung.',
          listeners=[("${execution.setVariable('nachgefasst', true)}", 'end')])
    p.add('GW_E', 'exclusiveGateway', 'Entscheidung?', 720, Y, label=(640, 262, 70), label_w=70)
    p.add('End_Aenderung', 'endEvent', 'Änderung gewünscht', 870, 190, label='right', label_w=80,
          listeners=[ergebnis('kundenentscheidungErgebnis', 'Änderung gewünscht')])
    p.add('End_Aufgeschoben', 'endEvent', 'Aufgeschoben', 870, 370, label='right', label_w=80,
          listeners=[ergebnis('kundenentscheidungErgebnis', 'Aufgeschoben'),
                     setze('kundenentscheidungGrund', 'Kunde: aufgeschoben')])
    p.add('End_Freigegeben', 'endEvent', 'Freigegeben', 870, Y, label='right', label_w=70,
          listeners=[ergebnis('kundenentscheidungErgebnis', 'Freigegeben')])
    p.add('XOR_NF', 'exclusiveGateway', '', 720, 440)
    p.add('End_NichtFreigegeben', 'endEvent', 'Nicht freigegeben', 870, 440, label='right', label_w=80,
          listeners=[ergebnis('kundenentscheidungErgebnis', 'Nicht freigegeben')])
    p.flow('F01', 'Start', 'S_Anfrage')
    p.flow('F02', 'S_Anfrage', 'XOR_W')
    p.flow('F03', 'XOR_W', 'R_Entscheidung')
    p.flow('F04', 'R_Entscheidung', 'GW_E')
    p.flow('F05', 'GW_E', 'End_Aenderung', 'top', 'left', via=[(720, 190)], name='Änderung gewünscht',
           cond="${entscheidung == 'AENDERN'}", label=(652, 204, 64))
    p.flow('F06', 'GW_E', 'End_Aufgeschoben', 'bottom', 'left', via=[(720, 370)],
           name='Aufgeschoben', cond="${entscheidung == 'AUFSCHIEBEN'}", label=(732, 348, 80))
    p.flow('F07', 'GW_E', 'End_Freigegeben', name='Freigegeben', cond="${entscheidung == 'FREIGEBEN'}",
           label=(750, 306, 80))
    p.flow('F08', 'GW_E', 'XOR_NF', 'bottom', 'top', name='Abgelehnt', cond="${entscheidung == 'ABLEHNEN'}",
           label=(726, 392, 60), listeners=[setze('kundenentscheidungGrund', 'Kunde: abgelehnt')])
    p.flow('F09', 'B_Frist', 'GW_Nach', 'bottom', 'top')
    p.flow('F10', 'GW_Nach', 'S_Nachfassen', 'bottom', 'top', name='Nein', cond='${!nachgefasst}', label=(568, 470, 30))
    p.flow('F11', 'S_Nachfassen', 'XOR_W', 'left', 'bottom', via=[(430, 540)])
    p.flow('F12', 'GW_Nach', 'XOR_NF', name='Ja (keine Antwort)', cond='${nachgefasst}', label=(592, 418, 110),
           listeners=[setze('kundenentscheidungGrund', 'Kunde: keine Antwort trotz Nachfassen')])
    p.flow('F13', 'XOR_NF', 'End_NichtFreigegeben')
    c = Collab('Collab_T2_Kundenentscheidung')
    c.participant('P_PflegeApp', APP, 60, 10, 960, 50)
    c.participant('P_Kundenentscheidung', 'Kundenentscheidung (gemeinsamer Baustein) - ' + T2, 60, 100, 960, 520,
                  process=p.id)
    c.participant('P_Team3', TEAM3, 60, 660, 960, 60)
    c.msg('M01', N_ANFRAGE, 'S_Anfrage', 'P_PflegeApp', [(300, 260), (300, 60)], (306, 150, 52))
    c.msg('M02', N_ENTSCHEIDUNG, 'P_PflegeApp', 'R_Entscheidung', [(560, 60), (560, 260)], (566, 150, 52))
    c.msg('M03', N_NACHFASS, 'S_Nachfassen', 'P_Team3', [(560, 580), (560, 660)], (566, 626, 52))
    build(f'{OUT}/T2_Kundenentscheidung.bpmn', c, [p], [('Msg_Kundenentscheidung', 'PflegeApp_Kundenentscheidung_Team2')], HDR)


# ---------------------------------------------------------------- Bestellabwicklung
def bestellabwicklung():
    p = Process('T2_Bestellabwicklung', 'Bestellabwicklung',
                doc='Teilprozess zu Schritt 8 und 9. Happy Path als Empfangsaufgabe mit angehängtem Timer. Nicht verfügbar '
                    'oder keine Antwort trotz Nachfassen -> Ersatzoption prüfen -> Ersatz erforderlich oder Keine Bestellung '
                    'möglich (Stiehl Punkt 7). Pflichtpunkt: Sendeaufgabe -> JMS-Queue (Camel/CBR), Antwort über Camel.')
    Y = 240
    p.add('Start', 'startEvent', 'Bestellung freigegeben', 205, Y, label_w=90,
          listeners=["${execution.setVariable('nachgefasst', false)}"])
    p.add('S_Bestellung', 'sendTask', 'Bestellung übermitteln', 330, Y, topic='t2-bestellung-senden', integration=True,
          doc='Bestellnachricht in JMS-Queue; Camel routet per CBR an den simulierten Lieferdienst.')
    p.add('XOR_W', 'exclusiveGateway', '', 470, Y)
    p.add('R_Antwort', 'receiveTask', 'Bestellantwort empfangen', 590, Y, message='Msg_Bestellantwort', integration=True,
          doc='Antwort des Lieferanten über Camel. bestellantwortStatus: BESTAETIGT oder NICHT_VERFUEGBAR.')
    p.add('B_Frist', 'boundaryEvent', 'Antwortfrist abgelaufen (1 Tag)', 590, 280, attached='R_Antwort', ev='timer',
          timer=('timeDuration', 'P1D'), label=(486, 290, 96), label_w=96, doc=PA + 'Antwortfrist Lieferant 1 Tag.')
    p.add('GW_A', 'exclusiveGateway', 'Bestellung bestätigt?', 740, Y, label='top', label_w=80)
    p.add('End_Bestaetigt', 'endEvent', 'Bestellung bestätigt', 1130, Y, label='right', label_w=70,
          listeners=[ergebnis('bestellabwicklungErgebnis', 'Bestellung bestätigt')])
    p.add('GW_N', 'exclusiveGateway', 'Bereits nachgefasst?', 590, 380, label=(486, 392, 90), label_w=90)
    p.add('S_Nachfassen', 'sendTask', 'Nachfassen beauftragen', 590, 480, topic='t2-nachfassen-beauftragen', integration=True,
          doc='Kommunikationsauftrag an Team 3. Schnittstelle = Vorschlag.',
          listeners=[("${execution.setVariable('nachgefasst', true)}", 'end')])
    p.add('XOR_E', 'exclusiveGateway', '', 740, 380)
    p.add('T_Ersatz', 'serviceTask', 'Ersatzoption prüfen', 880, 380, topic='t2-ersatzoption-pruefen',
          doc='Gibt es eine hinterlegte, zugelassene Ersatzoption und ist anzahlBestellversuche < 2? Ergebnis ersatzMoeglich. '
              'Begrenzt die Ersatz-Schleife im Hauptprozess. Kein medizinischer Ersatz.')
    p.add('GW_Ers', 'exclusiveGateway', 'Ersatz möglich?', 1020, 380, label='top', label_w=80)
    p.add('End_Ersatz', 'endEvent', 'Ersatz erforderlich', 1130, 380, label='right', label_w=70,
          listeners=[ergebnis('bestellabwicklungErgebnis', 'Ersatz erforderlich')])
    p.add('End_KeineBestellung', 'endEvent', 'Keine Bestellung möglich', 1130, 490, label='right', label_w=90,
          listeners=[ergebnis('bestellabwicklungErgebnis', 'Keine Bestellung möglich')])
    p.flow('F01', 'Start', 'S_Bestellung')
    p.flow('F02', 'S_Bestellung', 'XOR_W')
    p.flow('F03', 'XOR_W', 'R_Antwort')
    p.flow('F04', 'R_Antwort', 'GW_A')
    p.flow('F05', 'GW_A', 'End_Bestaetigt', name='Ja', cond="${bestellantwortStatus == 'BESTAETIGT'}", label=(770, 220, 30))
    p.flow('F06', 'GW_A', 'XOR_E', 'bottom', 'top', name='Nicht verfügbar',
           cond="${bestellantwortStatus == 'NICHT_VERFUEGBAR'}", label=(748, 296, 70),
           listeners=[setze('ersatzGrund', 'Produkt nicht verfügbar')])
    p.flow('F07', 'B_Frist', 'GW_N', 'bottom', 'top')
    p.flow('F08', 'GW_N', 'S_Nachfassen', 'bottom', 'top', name='Nein', cond='${!nachgefasst}', label=(598, 410, 30))
    p.flow('F09', 'S_Nachfassen', 'XOR_W', 'left', 'bottom', via=[(470, 480)])
    p.flow('F10', 'GW_N', 'XOR_E', name='Ja', cond='${nachgefasst}', label=(630, 360, 30),
           listeners=[setze('ersatzGrund', 'Lieferant antwortet nicht')])
    p.flow('F11', 'XOR_E', 'T_Ersatz')
    p.flow('F12', 'T_Ersatz', 'GW_Ers')
    p.flow('F13', 'GW_Ers', 'End_Ersatz', name='Ja', cond='${ersatzMoeglich}', label=(1050, 360, 30))
    p.flow('F14', 'GW_Ers', 'End_KeineBestellung', 'bottom', 'left', via=[(1020, 490)], name='Nein', cond='${!ersatzMoeglich}',
           label=(1030, 468, 34))
    W = 1220
    c = Collab('Collab_T2_Bestellabwicklung')
    c.participant('P_Lieferant', LIEFERANT, 120, 20, W, 60)
    c.participant('P_Bestellabwicklung', 'Bestellabwicklung - ' + T2, 120, 120, W, 480, process=p.id)
    c.participant('P_Team3', TEAM3, 120, 640, W, 60)
    c.msg('M01', N_BESTELLUNG, 'S_Bestellung', 'P_Lieferant', [(330, 200), (330, 80)], (336, 130, 60))
    c.msg('M02', N_BANTWORT, 'P_Lieferant', 'R_Antwort', [(590, 80), (590, 200)], (596, 130, 60))
    c.msg('M03', N_NACHFASS, 'S_Nachfassen', 'P_Team3', [(590, 520), (590, 640)], (596, 608, 60))
    build(f'{OUT}/T2_Bestellabwicklung.bpmn', c, [p], [('Msg_Bestellantwort', 'Lieferant_Bestellantwort_Team2')], HDR)


# ---------------------------------------------------------------- Lieferprüfung
def lieferpruefung():
    p = Process('T2_Lieferpruefung', 'Lieferprüfung',
                doc='Teilprozess zu Schritt 9 und 10. Die Pflegeperson bestätigt über die Pflege-App. Jede Frist und jede '
                    'Abweichung geht an Team 3 (Klärung). Abgeschlossen nur bei bestätigter (Nach-)Lieferung.')
    Y = 280
    p.add('Start', 'startEvent', 'Bestellung bestätigt', 205, Y, label_w=90)
    p.add('R_Versand', 'receiveTask', 'Versandmeldung empfangen', 330, Y, message='Msg_Versandmeldung', integration=True,
          doc='Lieferant meldet Versand und erwartetes Lieferdatum (über Camel).')
    p.add('B_Versand', 'boundaryEvent', 'Versandfrist abgelaufen (5 Tage)', 300, 320, attached='R_Versand', ev='timer',
          timer=('timeDuration', 'P5D'), label=(196, 330, 96), label_w=96, doc=PA + 'Versandfrist 5 Tage.')
    p.add('S_Anfrage', 'sendTask', 'Lieferbestätigung anfordern', 490, Y, topic='t2-lieferbestaetigung-anfordern',
          integration=True, doc='Nachricht an die Pflege-App: erwarteter Inhalt und Liefertermin, Bitte um Bestätigung.')
    p.add('R_Bestaetigung', 'receiveTask', 'Lieferbestätigung empfangen', 650, Y, message='Msg_Lieferbestaetigung',
          integration=True, doc='lieferbefund: RICHTIG, TEILWEISE, FALSCH oder NICHT_GELIEFERT.')
    p.add('B_Bestaetigung', 'boundaryEvent', 'Bestätigungsfrist abgelaufen (3 Tage)', 680, 320, attached='R_Bestaetigung',
          ev='timer', timer=('timeDuration', 'P3D'), label=(690, 330, 90), label_w=90, doc=PA + 'Bestätigungsfrist 3 Tage.')
    p.add('GW_Korrekt', 'exclusiveGateway', 'Lieferung korrekt?', 800, Y, label='top', label_w=80)
    p.add('XOR_Ab', 'exclusiveGateway', '', 1200, Y)
    p.add('End_Abgeschlossen', 'endEvent', 'Lieferung abgeschlossen', 1600, Y, label='bottom', label_w=80,
          listeners=[ergebnis('lieferpruefungErgebnis', 'Lieferung abgeschlossen')])
    p.add('GW_Klaerung', 'exclusiveGateway', '', 800, 410)
    p.add('S_Klaerung', 'sendTask', 'Klärung beauftragen', 920, 410, topic='t2-klaerung-beauftragen', integration=True,
          doc='Abweichung erfassen, Gegenstelle über Team 3 kontaktieren; Status bleibt offen.')
    p.add('R_Klaerung', 'receiveTask', 'Klärungsergebnis empfangen', 1080, 410, message='Msg_Klaerungsergebnis',
          integration=True, doc='klaerungsergebnis = NACHLIEFERUNG_BESTAETIGT oder NICHT_GEKLAERT. Schnittstelle = Vorschlag.')
    p.add('B_Klaerung', 'boundaryEvent', 'Klärungsfrist abgelaufen (7 Tage)', 1110, 450, attached='R_Klaerung', ev='timer',
          timer=('timeDuration', 'P7D'), label=(1120, 460, 90), label_w=90, doc=PA + 'Sicherheitsfrist Klärung 7 Tage.')
    p.add('GW_Geklaert', 'exclusiveGateway', 'Nachlieferung bestätigt?', 1200, 410, label=(1108, 350, 86), label_w=86)
    p.add('XOR_Ue', 'exclusiveGateway', '', 1340, 410)
    p.add('T_Uebergeben', 'serviceTask', 'Klärungsfall übergeben', 1460, 410, topic='t2-klaerungsfall-uebergeben',
          doc='Übergabe an die menschliche Prüfstelle von Team 2 mit dokumentiertem Grund (Zustand: Übergeben).')
    p.add('End_Ungeklaert', 'endEvent', 'Lieferung ungeklärt', 1600, 410, label_w=80,
          listeners=[ergebnis('lieferpruefungErgebnis', 'Lieferung ungeklärt')])
    p.flow('F01', 'Start', 'R_Versand')
    p.flow('F02', 'R_Versand', 'S_Anfrage')
    p.flow('F03', 'S_Anfrage', 'R_Bestaetigung')
    p.flow('F04', 'R_Bestaetigung', 'GW_Korrekt')
    p.flow('F05', 'GW_Korrekt', 'XOR_Ab', name='Richtig geliefert', cond="${lieferbefund == 'RICHTIG'}", label=(830, 260, 90))
    p.flow('F06', 'GW_Korrekt', 'GW_Klaerung', 'bottom', 'top', name='Abweichung festgestellt',
           cond="${lieferbefund != 'RICHTIG'}", label=(808, 330, 70))
    p.flow('F07', 'B_Versand', 'GW_Klaerung', 'bottom', 'bottom', via=[(300, 500), (800, 500)])
    p.flow('F08', 'B_Bestaetigung', 'GW_Klaerung', 'bottom', 'left', via=[(680, 410)])
    p.flow('F09', 'GW_Klaerung', 'S_Klaerung')
    p.flow('F10', 'S_Klaerung', 'R_Klaerung')
    p.flow('F11', 'R_Klaerung', 'GW_Geklaert')
    p.flow('F12', 'GW_Geklaert', 'XOR_Ab', 'top', 'bottom', name='Ja',
           cond="${klaerungsergebnis == 'NACHLIEFERUNG_BESTAETIGT'}", label=(1208, 330, 20))
    p.flow('F13', 'GW_Geklaert', 'XOR_Ue', name='Nein', cond="${klaerungsergebnis != 'NACHLIEFERUNG_BESTAETIGT'}",
           label=(1232, 392, 30))
    p.flow('F14', 'B_Klaerung', 'XOR_Ue', 'bottom', 'bottom', via=[(1110, 520), (1340, 520)])
    p.flow('F15', 'XOR_Ab', 'End_Abgeschlossen')
    p.flow('F16', 'XOR_Ue', 'T_Uebergeben')
    p.flow('F17', 'T_Uebergeben', 'End_Ungeklaert')
    W = 1560
    c = Collab('Collab_T2_Lieferpruefung')
    c.participant('P_Lieferant', LIEFERANT, 120, 10, W, 50)
    c.participant('P_PflegeApp', APP, 420, 70, W - 300, 50)
    c.participant('P_Lieferpruefung', 'Lieferprüfung - ' + T2, 120, 160, W, 400, process=p.id)
    c.participant('P_Team3', TEAM3, 120, 610, W, 60)
    c.msg('M01', N_VERSAND, 'P_Lieferant', 'R_Versand', [(330, 60), (330, 240)], (336, 170, 60))
    c.msg('M02', N_BANFRAGE, 'S_Anfrage', 'P_PflegeApp', [(490, 240), (490, 120)], (496, 170, 76))
    c.msg('M03', N_LBEST, 'P_PflegeApp', 'R_Bestaetigung', [(650, 120), (650, 240)], (656, 170, 70))
    c.msg('M04', N_KAUFTRAG, 'S_Klaerung', 'P_Team3', [(920, 450), (920, 610)], (926, 580, 60))
    c.msg('M05', N_KERGEBNIS, 'P_Team3', 'R_Klaerung', [(1040, 610), (1040, 450)], (1046, 580, 60))
    build(f'{OUT}/T2_Lieferpruefung.bpmn', c, [p],
          [('Msg_Versandmeldung', 'Lieferant_Versandmeldung_Team2'),
           ('Msg_Lieferbestaetigung', 'PflegeApp_Lieferbestaetigung_Team2'),
           ('Msg_Klaerungsergebnis', 'Team3_Klaerungsergebnis_Team2')], HDR)


for fn in (hauptprozess, bestellfreigabe, kundenentscheidung, bestellabwicklung, lieferpruefung):
    fn()
print('ok', sorted(f for f in os.listdir(OUT) if f.endswith('.bpmn')))
