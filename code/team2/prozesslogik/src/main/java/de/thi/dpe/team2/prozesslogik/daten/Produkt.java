// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;

/** Verbrauchsprodukt mit Packungsgröße und aktuellem Preis. */
@Entity
@Table(name = "t2_produkt")
public class Produkt {
    @Id
    @Column(length = 20)
    public String id;

    @Column(nullable = false, length = 100)
    public String name;

    @Column(nullable = false, length = 100)
    public String kategorie;

    /** Stück je Packung. */
    @Column(nullable = false)
    public int packungsgroesse;

    @Column(name = "preis_packung", nullable = false, precision = 8, scale = 2)
    public BigDecimal preisPackung;

    @Column(nullable = false)
    public boolean verfuegbar;

    @Column(name = "lieferant_id", nullable = false, length = 20)
    public String lieferantId;
}

