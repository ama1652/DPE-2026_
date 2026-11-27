// Verantwortlich: Saifudin Mohammadi
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.benachrichtigung;

import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

/** Schlüssel ist die vorgangId (String), deshalb PanacheRepositoryBase. */
@ApplicationScoped
public class VorgangStatusRepository implements PanacheRepositoryBase<VorgangStatus, String> {
}
// KI-generiert (Claude, Anthropic) - Ende
