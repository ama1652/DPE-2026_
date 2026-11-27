// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;

@ApplicationScoped
public class BestandRepository implements PanacheRepository<Bestand> {

    /** Die letzten Einträge, neuester zuerst (für Ist-Bestand und beobachteten Verbrauch). */
    public List<Bestand> letzte(String pflegehaushaltId, String produktId, int anzahl) {
        return find("pflegehaushaltId = ?1 and produktId = ?2 order by zeitpunkt desc", pflegehaushaltId, produktId)
                .page(0, anzahl).list();
    }
}

