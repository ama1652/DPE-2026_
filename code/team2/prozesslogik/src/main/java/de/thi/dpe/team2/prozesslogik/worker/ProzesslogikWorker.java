// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik.worker;

import de.thi.dpe.team2.prozesslogik.ProzesslogikService;
import io.quarkus.runtime.ShutdownEvent;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;
import org.camunda.bpm.client.ExternalTaskClient;
import org.camunda.bpm.client.task.ExternalTask;
import org.camunda.bpm.client.task.ExternalTaskService;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

/**
 * External-Task-Worker für die Service-Aufgaben der Prozesslogik (CIB seven):
 * <ul>
 *   <li>t2-vorgang-pruefen          (Hauptprozess, "Laufenden Vorgang prüfen")</li>
 *   <li>t2-reichweite-berechnen     (Hauptprozess, "Verbrauch und Reichweite berechnen")</li>
 *   <li>t2-vorschlag-erstellen      (Bestellfreigabe, "Produkt und Menge vorschlagen")</li>
 *   <li>t2-ersatzoption-pruefen     (Bestellabwicklung, "Ersatzoption prüfen")</li>
 *   <li>t2-bestand-fortschreiben    (Hauptprozess, "Bestand und Verbrauch fortschreiben")</li>
 * </ul>
 * Die beiden Regelaufgaben laufen als DMN direkt in der Engine (decisionRef) und brauchen keinen Worker.
 */
@ApplicationScoped
public class ProzesslogikWorker {

    private static final Logger LOG = Logger.getLogger(ProzesslogikWorker.class);

    @Inject
    ProzesslogikService service;

    @ConfigProperty(name = "team2.engine.rest-url")
    String restUrl;
    @ConfigProperty(name = "team2.worker.id")
    String workerId;
    @ConfigProperty(name = "team2.worker.lock-dauer-ms")
    long lockDauer;
    @ConfigProperty(name = "team2.worker.wiederholungen")
    int wiederholungen;

    private ExternalTaskClient client;

    void starten(@Observes StartupEvent ev) {
        client = ExternalTaskClient.create().baseUrl(restUrl).workerId(workerId).asyncResponseTimeout(10_000).build();
        abonnieren("t2-vorgang-pruefen", service::vorgangPruefen);
        abonnieren("t2-reichweite-berechnen", service::reichweiteBerechnen);
        abonnieren("t2-vorschlag-erstellen", service::vorschlagErstellen);
        abonnieren("t2-ersatzoption-pruefen", service::ersatzoptionPruefen);
        abonnieren("t2-bestand-fortschreiben", service::bestandFortschreiben);
        LOG.infof("Prozesslogik-Worker gestartet (%s)", restUrl);
    }

    void stoppen(@Observes ShutdownEvent ev) {
        if (client != null) {
            client.stop();
        }
    }

    private void abonnieren(String topic, Function<Map<String, Object>, Map<String, Object>> logik) {
        client.subscribe(topic).lockDuration(lockDauer).handler((task, ts) -> bearbeiten(task, ts, logik)).open();
    }

    private void bearbeiten(ExternalTask task, ExternalTaskService ts,
                            Function<Map<String, Object>, Map<String, Object>> logik) {
        try {
            Map<String, Object> ergebnis = logik.apply(variablen(task));
            ts.complete(task, ergebnis);
            LOG.infof("%s erledigt (Instanz %s): %s", task.getTopicName(), task.getProcessInstanceId(), ergebnis);
        } catch (RuntimeException e) {
            int rest = task.getRetries() == null ? wiederholungen : task.getRetries() - 1;
            LOG.errorf(e, "%s fehlgeschlagen, verbleibende Versuche: %d", task.getTopicName(), rest);
            ts.handleFailure(task, task.getTopicName() + " fehlgeschlagen: " + e.getMessage(), e.toString(),
                    Math.max(rest, 0), 10_000L);
        }
    }

    private static Map<String, Object> variablen(ExternalTask task) {
        Map<String, Object> v = new HashMap<>(task.getAllVariables());
        if (task.getBusinessKey() != null) {
            v.put("businessKey", task.getBusinessKey());
        }
        return v;
    }
}
// KI-generiert (Claude, Anthropic) - Ende
