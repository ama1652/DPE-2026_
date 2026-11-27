// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik.daten;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

/** Ein Bestandseintrag. Der jüngste Eintrag je Haushalt und Produkt ist der Ist-Bestand (Team 2 ist führendes System). */
@Entity
@Table(name = "t2_bestand")
public class Bestand {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;

    @Column(name = "pflegehaushalt_id", nullable = false, length = 20)
    public String pflegehaushaltId;

    @Column(name = "produkt_id", nullable = false, length = 20)
    public String produktId;

    /** Ist-Bestand in Stück. */
    @Column(nullable = false)
    public int menge;

    @Column(nullable = false)
    public LocalDateTime zeitpunkt;

    /** Fortschreibung, Meldung Pflege-App oder Testdaten. */
    @Column(nullable = false, length = 40)
    public String herkunft;
}
// KI-generiert (Claude, Anthropic) - Ende
