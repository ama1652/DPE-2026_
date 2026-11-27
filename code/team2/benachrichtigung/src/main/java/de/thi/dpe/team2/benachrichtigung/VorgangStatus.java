// Verantwortlich: Saifudin Mohammadi
package de.thi.dpe.team2.benachrichtigung;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

/**
 * Letzter gemeinsamer Vorgangszustand (Integrationspaket 6.3) je Vorgang.
 * Wird bei jedem Ergebnis fortgeschrieben, auch bei Abbrüchen (Stiehl, Rückmeldung Punkt 3).
 * Abstimmen mit dem Datenmodell aus T2-03 (Erion); bis dahin eigene Tabelle.
 */
@Entity
@Table(name = "t2_vorgang_status")
public class VorgangStatus {

    /** Business Key des Vorgangs, z. B. PH-0001:TP-M. */
    @Id
    @Column(length = 60)
    private String vorgangId;

    @Column(nullable = false, length = 40)
    private String pflegehaushaltId;

    /** z. B. Erfolgreich abgeschlossen, Erfolglos abgeschlossen, Übergeben. */
    @Column(nullable = false, length = 40)
    private String zustand;

    /** Fachliches Ergebnis = Name des Endereignisses, z. B. "Bestellung aufgeschoben". */
    @Column(nullable = false, length = 80)
    private String ergebnis;

    @Column(length = 300)
    private String grund;

    @Column(nullable = false)
    private LocalDateTime aktualisiert;

    protected VorgangStatus() {
        // für JPA
    }

    public VorgangStatus(String vorgangId, String pflegehaushaltId) {
        this.vorgangId = vorgangId;
        this.pflegehaushaltId = pflegehaushaltId;
    }

    public void fortschreiben(String zustand, String ergebnis, String grund) {
        this.zustand = zustand;
        this.ergebnis = ergebnis;
        this.grund = grund;
        this.aktualisiert = LocalDateTime.now();
    }

    public String getVorgangId() { return vorgangId; }
    public String getPflegehaushaltId() { return pflegehaushaltId; }
    public String getZustand() { return zustand; }
    public String getErgebnis() { return ergebnis; }
    public String getGrund() { return grund; }
    public LocalDateTime getAktualisiert() { return aktualisiert; }
}

