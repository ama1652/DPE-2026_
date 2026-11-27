// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** Rechenregeln mit den Zahlen der Testfälle aus testdaten/team2. */
class RechnerTest {

    @Test
    void tf01VorschlagDreiPackungen() {
        var v = Rechner.vorschlag("TP-M", "Testprodukt M", "LF-0001", 30, new BigDecimal("24.90"), 120, 30,
                "TP-M", "LF-0001", true);
        assertEquals(3, v.packungen());
        assertEquals(90, v.stueck());
        assertEquals(0, v.preisGesamt().compareTo(new BigDecimal("74.70")));
        assertFalse(v.produktGewechselt());
        assertFalse(v.lieferantGewechselt());
    }

    @Test
    void tf11ErsatzproduktIstProduktwechsel() {
        var v = Rechner.vorschlag("TP-M-PLUS", "Testprodukt M Plus", "LF-0001", 30, new BigDecimal("26.40"), 120, 30,
                "TP-M", "LF-0001", true);
        assertTrue(v.produktGewechselt());
        assertEquals(0, v.preisGesamt().compareTo(new BigDecimal("79.20")));
    }

    @Test
    void verbrauchssprungAbFaktor15() {
        LocalDateTime jetzt = LocalDateTime.of(2026, 12, 1, 8, 0);
        assertTrue(Rechner.verbrauchssprung(4, 90, jetzt.minusDays(5), 30, jetzt));   // 12 Stück/Tag
        assertFalse(Rechner.verbrauchssprung(4, 50, jetzt.minusDays(5), 30, jetzt));  // 4 Stück/Tag
        assertFalse(Rechner.verbrauchssprung(4, null, null, 30, jetzt));               // keine Historie
        assertFalse(Rechner.verbrauchssprung(4, 20, jetzt.minusDays(5), 110, jetzt));  // Zugang
    }

    @Test
    void ersatzSchleifeIstBegrenzt() {
        assertTrue(Rechner.ersatzMoeglich("TP-M-PLUS", true, 1));
        assertFalse(Rechner.ersatzMoeglich("TP-M-PLUS", true, 2));
        assertFalse(Rechner.ersatzMoeglich("TP-M-PLUS", false, 1));
        assertFalse(Rechner.ersatzMoeglich(null, true, 1));
    }

    @Test
    void kennungAusBusinessKey() {
        var k = ProzesslogikService.kennung(Map.of("businessKey", "PH-0001:TP-M"));
        assertEquals("PH-0001", k.haushalt());
        assertEquals("TP-M", k.produkt());
    }
}
// KI-generiert (Claude, Anthropic) - Ende
