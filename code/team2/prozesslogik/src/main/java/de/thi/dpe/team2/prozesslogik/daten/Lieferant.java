// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/** Lieferant (Testdaten: LF-0001 Versorgungsdienst Beispiel). Tabelle wie in testdaten/team2/T2_Testdaten.sql. */
@Entity
@Table(name = "t2_lieferant")
public class Lieferant {
    @Id
    @Column(length = 20)
    public String id;

    @Column(nullable = false, length = 100)
    public String name;

    @Column(name = "lieferzeit_tage", nullable = false)
    public int lieferzeitTage;
}

