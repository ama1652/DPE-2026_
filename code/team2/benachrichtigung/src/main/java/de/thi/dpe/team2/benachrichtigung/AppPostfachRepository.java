// Verantwortlich: Saifudin Mohammadi
package de.thi.dpe.team2.benachrichtigung;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

/** Panache im Repository-Stil (Vorgabe aus der Vorlesung: kein "extends PanacheEntity"). */
@ApplicationScoped
public class AppPostfachRepository implements PanacheRepository<AppNachricht> {

    public List<AppNachricht> fuerVorgang(String vorgangId) {
        return list("vorgangId = ?1 order by zeitpunkt", vorgangId);
    }
}

