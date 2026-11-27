// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;

/** Versorgungsprofil (Teamauftrag 2, Abschnitt 6): bevorzugtes Produkt, Ersatzoption, Ziel- und Mindestbestand. */
@Entity
@Table(name = "t2_versorgungsprofil")
public class Versorgungsprofil {
    @Id
    @Column(length = 20)
    public String id;

    @Column(name = "pflegehaushalt_id", nullable = false, length = 20)
    public String pflegehaushaltId;

    /** Bevorzugtes Produkt. */
    @Column(name = "produkt_id", nullable = false, length = 20)
    public String produktId;

    /** Hinterlegte Ersatzoption (kein medizinischer Ersatz), darf fehlen. */
    @Column(name = "ersatz_produkt_id", length = 20)
    public String ersatzProduktId;

    @Column(nullable = false)
    public int zielbestand;

    @Column(nullable = false)
    public int mindestbestand;

    @Column(name = "verbrauch_pro_tag", nullable = false, precision = 6, scale = 2)
    public BigDecimal verbrauchProTag;

    @Column(name = "verbrauch_herkunft", nullable = false, length = 40)
    public String verbrauchHerkunft;

    /** Gesamtpreis je Bestellung, darüber Kundenfreigabe (DMN Berechtigungsregel). */
    @Column(nullable = false, precision = 8, scale = 2)
    public BigDecimal preisgrenze;

    @Column(name = "pruefintervall_tage", nullable = false)
    public int pruefintervallTage;
}

