// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Optional;

/**
 * Lesezugriff auf Versorgungsprofile (Panache im Repository-Stil, kein "extends PanacheEntity").
 * Abgleichen mit dem Datenmodell aus T2-03 (Erion).
 */
@ApplicationScoped
public class StammdatenRepository implements PanacheRepositoryBase<Versorgungsprofil, String> {

    public Optional<Versorgungsprofil> profil(String pflegehaushaltId, String produktId) {
        return find("pflegehaushaltId = ?1 and (produktId = ?2 or ersatzProduktId = ?2)", pflegehaushaltId, produktId)
                .firstResultOptional();
    }
}

