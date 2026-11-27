// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
package de.thi.dpe.team2.prozesslogik.daten;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ProduktRepository implements PanacheRepositoryBase<Produkt, String> {
}

