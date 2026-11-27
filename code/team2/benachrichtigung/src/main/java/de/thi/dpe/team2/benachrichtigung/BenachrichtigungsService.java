// Verantwortlich: Saifudin Mohammadi
package de.thi.dpe.team2.benachrichtigung;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import java.util.Map;

/**
 * Fachlogik der Benachrichtigungen an die Pflege-App (Teamauftrag 2.2: Team 2 stellt Benachrichtigungen bereit).
 * Kennt keine Engine-Klassen: Der Worker übergibt nur Prozessvariablen als Map.
 */
@ApplicationScoped
public class BenachrichtigungsService {

    /** Endereignis bzw. Aufgabe im Hauptprozess -> fachliches Ergebnis (Label-Matching mit dem BPMN). */
    static final Map<String, String> ERGEBNIS_JE_ELEMENT = Map.of(
            "SA_Ergebnis", "Nachversorgung abgeschlossen",
            "End_NichtFreigegeben", "Bestellung nicht freigegeben",
            "End_Aufgeschoben", "Bestellung aufgeschoben",
            "End_NichtZulaessig", "Bestellung nicht zulässig",
            "End_KeineBestellung", "Keine Bestellung möglich",
            "End_Ungeklaert", "Lieferung ungeklärt");

    @Inject
    AppPostfachRepository postfach;

    @Inject
    VorgangStatusRepository vorgaenge;

    /** Topic t2-freigabeanfrage-senden (Teilprozess Kundenentscheidung). */
    @Transactional
    public AppNachricht freigabeanfrageSenden(Map<String, Object> v, String prozessinstanzId) {
        String text = "Bitte entscheiden Sie: " + text(v, "freigabeHandlung", "geplante Bestellung")
                + "\nGrund: " + text(v, "freigabeBegruendung", "Abweichung vom Versorgungsprofil")
                + "\nWenn Sie nicht freigeben: " + text(v, "freigabeFolgen", "Die Bestellung wird nicht ausgelöst.")
                + gueltigBis(v)
                + "\nAntwortmöglichkeiten: Freigeben, Ändern, Ablehnen, Aufschieben.";
        return speichern(v, AppNachricht.Typ.FREIGABEANFRAGE, "Freigabe erforderlich", text, prozessinstanzId);
    }

    /** Topic t2-lieferbestaetigung-anfordern (Teilprozess Lieferprüfung). */
    @Transactional
    public AppNachricht lieferbestaetigungAnfordern(Map<String, Object> v, String prozessinstanzId) {
        String text = "Ihre Lieferung ist unterwegs: " + text(v, "bestellung", "bestellte Verbrauchsprodukte")
                + "\nBitte bestätigen Sie nach Erhalt: richtig, teilweise, falsch oder nicht geliefert.";
        return speichern(v, AppNachricht.Typ.LIEFERBESTAETIGUNG_ANFRAGE, "Bitte Lieferung bestätigen", text,
                prozessinstanzId);
    }

    /**
     * Topic t2-ergebnis-mitteilen: Erfolg (Sendeaufgabe im Vorgangsabschluss) und jeder Abbruch
     * (Nachrichten-Endereignisse). Schreibt immer auch den Vorgangszustand fort.
     */
    @Transactional
    public AppNachricht ergebnisMitteilen(Map<String, Object> v, String elementId, String prozessinstanzId) {
        String ergebnis = ERGEBNIS_JE_ELEMENT.getOrDefault(elementId, "Vorgang beendet");
        boolean erfolg = "SA_Ergebnis".equals(elementId);
        // Bei SA_Ergebnis setzt das Endereignis den Zustand erst danach, deshalb hier ableiten
        String zustand = erfolg ? "Erfolgreich abgeschlossen" : text(v, "vorgangszustand", "Erfolglos abgeschlossen");
        String grund = erfolg ? null : grund(v, elementId);

        StringBuilder text = new StringBuilder("Ergebnis: ").append(ergebnis).append('.');
        if (grund != null) {
            text.append("\nGrund: ").append(grund);
        }
        if (!erfolg) {
            text.append("\nEs wurde nichts bestellt. ").append(reichweitenrisiko(v));
        } else {
            text.append("\nIhr Bestand wurde aktualisiert.");
        }

        String vorgangId = vorgangId(v);
        VorgangStatus status = vorgaenge.findByIdOptional(vorgangId)
                .orElseGet(() -> new VorgangStatus(vorgangId, text(v, "pflegehaushaltId", "unbekannt")));
        status.fortschreiben(zustand, ergebnis, grund);
        vorgaenge.persist(status);

        return speichern(v, AppNachricht.Typ.ERGEBNIS, ergebnis, text.toString(), prozessinstanzId);
    }

    // ------------------------------------------------------------------ Hilfen

    private AppNachricht speichern(Map<String, Object> v, AppNachricht.Typ typ, String betreff, String text,
                                   String prozessinstanzId) {
        AppNachricht n = new AppNachricht(text(v, "pflegehaushaltId", "unbekannt"), vorgangId(v), typ, betreff, text,
                prozessinstanzId);
        postfach.persist(n);
        return n;
    }

    private static String grund(Map<String, Object> v, String elementId) {
        return switch (elementId) {
            case "End_KeineBestellung" -> text(v, "ersatzGrund", "Kein zugelassener Ersatz verfügbar");
            case "End_Ungeklaert" -> "Lieferung konnte nicht geklärt werden, an die Prüfstelle übergeben";
            default -> text(v, "ablehnungsgrund", null);
        };
    }

    /** Reichweitenrisiko sichtbar machen (Teamauftrag 2, Abschnitt 5). */
    static String reichweitenrisiko(Map<String, Object> v) {
        Double bestand = zahl(v.get("istBestand"));
        Double verbrauch = zahl(v.get("verbrauchProTag"));
        if (bestand == null || verbrauch == null || verbrauch <= 0) {
            return "Bitte prüfen Sie Ihren Vorrat.";
        }
        long tage = (long) Math.floor(bestand / verbrauch);
        return "Ihr Vorrat reicht voraussichtlich noch " + tage + (tage == 1 ? " Tag." : " Tage.");
    }

    private static String vorgangId(Map<String, Object> v) {
        return text(v, "vorgangId", text(v, "businessKey", "unbekannt"));
    }

    private static String gueltigBis(Map<String, Object> v) {
        String bis = text(v, "freigabeGueltigBis", null);
        return bis == null ? "" : "\nGültig bis: " + bis;
    }

    static String text(Map<String, Object> v, String name, String ersatz) {
        Object o = v.get(name);
        return (o == null || o.toString().isBlank()) ? ersatz : o.toString();
    }

    private static Double zahl(Object o) {
        if (o instanceof Number n) {
            return n.doubleValue();
        }
        try {
            return o == null ? null : Double.valueOf(o.toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}

