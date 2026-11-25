// Verantwortlich: Saifudin Mohammadi
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.benachrichtigung;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

/**
 * Eine Nachricht im simulierten Postfach der Pflege-App (Integrationspaket 7.5: Simulation sichtbar gekennzeichnet).
 * Später ersetzt die echte Pflege-App dieses Postfach; Felder bleiben gleich.
 */
@Entity
@Table(name = "t2_app_postfach")
public class AppNachricht {

    public enum Typ { FREIGABEANFRAGE, LIEFERBESTAETIGUNG_ANFRAGE, ERGEBNIS }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 40)
    private String pflegehaushaltId;

    @Column(length = 60)
    private String vorgangId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private Typ typ;

    @Column(nullable = false, length = 200)
    private String betreff;

    @Column(nullable = false, length = 2000)
    private String text;

    @Column(nullable = false)
    private LocalDateTime zeitpunkt;

    /** Immer true, solange die Pflege-App simuliert wird. */
    @Column(nullable = false)
    private boolean simulation = true;

    /** Prozessinstanz, für die Nachverfolgung im Cockpit. */
    @Column(length = 64)
    private String prozessinstanzId;

    protected AppNachricht() {
        // für JPA
    }

    public AppNachricht(String pflegehaushaltId, String vorgangId, Typ typ, String betreff, String text,
                        String prozessinstanzId) {
        this.pflegehaushaltId = pflegehaushaltId;
        this.vorgangId = vorgangId;
        this.typ = typ;
        this.betreff = betreff;
        this.text = text;
        this.prozessinstanzId = prozessinstanzId;
        this.zeitpunkt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public String getPflegehaushaltId() { return pflegehaushaltId; }
    public String getVorgangId() { return vorgangId; }
    public Typ getTyp() { return typ; }
    public String getBetreff() { return betreff; }
    public String getText() { return text; }
    public LocalDateTime getZeitpunkt() { return zeitpunkt; }
    public boolean isSimulation() { return simulation; }
    public String getProzessinstanzId() { return prozessinstanzId; }
}
// KI-generiert (Claude, Anthropic) - Ende
