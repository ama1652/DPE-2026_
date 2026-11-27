// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;

/**
 * Reine Rechenregeln ohne Datenbank und Engine, damit sie einzeln testbar sind.
 * Alle Schwellen sind Projektannahmen (nicht von Prof. Stiehl vorgegeben).
 */
public final class Rechner {

    /** Ab diesem Faktor gegenüber der Verbrauchsannahme gilt der Verbrauch als "deutlich verändert" (Annahme). */
    public static final double SPRUNG_FAKTOR = 1.5;

    /** Höchstens so viele Bestellversuche (1. Versuch + 1 Ersatz), Stiehl Punkt 7. */
    public static final int MAX_BESTELLVERSUCHE = 2;

    private Rechner() {
    }

    /**
     * Verbrauchssprung: beobachteter Verbrauch zwischen zwei Bestandseinträgen gegenüber der Annahme im Profil.
     * Ohne zweiten Eintrag oder bei Zugang (Bestand gestiegen) kein Sprung.
     */
    public static boolean verbrauchssprung(double verbrauchAnnahme, Integer altMenge, LocalDateTime altZeit,
                                           int neuMenge, LocalDateTime neuZeit) {
        if (altMenge == null || altZeit == null || neuZeit == null || verbrauchAnnahme <= 0) {
            return false;
        }
        double tage = Duration.between(altZeit, neuZeit).toHours() / 24.0;
        if (tage < 1 || neuMenge > altMenge) {
            return false;
        }
        double beobachtet = (altMenge - neuMenge) / tage;
        return beobachtet >= verbrauchAnnahme * SPRUNG_FAKTOR;
    }

    /** Ergebnis von "Produkt und Menge vorschlagen". */
    public record Vorschlag(String produktId, String produktName, String lieferantId, int packungen, int stueck,
                            BigDecimal preisGesamt, boolean produktHinterlegt, boolean produktGewechselt,
                            boolean lieferantGewechselt) {
    }

    /**
     * Menge = Zielbestand - Ist-Bestand, aufgerundet auf volle Packungen (mindestens 1 Packung).
     *
     * @param bevorzugtLieferantId Lieferant des bevorzugten Produkts (für "Lieferant gewechselt?")
     * @param hinterlegt           ob das vorgeschlagene Produkt im Versorgungsprofil steht
     */
    public static Vorschlag vorschlag(String produktId, String produktName, String lieferantId, int packungsgroesse,
                                      BigDecimal preisPackung, int zielbestand, int istBestand,
                                      String bevorzugtProduktId, String bevorzugtLieferantId, boolean hinterlegt) {
        int fehlend = Math.max(zielbestand - istBestand, 1);
        int packungen = (int) Math.ceil(fehlend / (double) Math.max(packungsgroesse, 1));
        packungen = Math.max(packungen, 1);
        int stueck = packungen * packungsgroesse;
        BigDecimal preis = preisPackung.multiply(BigDecimal.valueOf(packungen)).setScale(2, RoundingMode.HALF_UP);
        return new Vorschlag(produktId, produktName, lieferantId, packungen, stueck, preis, hinterlegt,
                !produktId.equals(bevorzugtProduktId), !lieferantId.equals(bevorzugtLieferantId));
    }

    /** "Ersatzoption prüfen": Ersatz hinterlegt, verfügbar und Obergrenze der Versuche noch nicht erreicht. */
    public static boolean ersatzMoeglich(String ersatzProduktId, boolean ersatzVerfuegbar, int anzahlBestellversuche) {
        return ersatzProduktId != null && !ersatzProduktId.isBlank() && ersatzVerfuegbar
                && anzahlBestellversuche < MAX_BESTELLVERSUCHE;
    }

    /** Reichweite in ganzen Tagen. */
    public static long reichweiteTage(int istBestand, double verbrauchProTag) {
        return verbrauchProTag <= 0 ? Long.MAX_VALUE : (long) Math.floor(istBestand / verbrauchProTag);
    }
}
// KI-generiert (Claude, Anthropic) - Ende
