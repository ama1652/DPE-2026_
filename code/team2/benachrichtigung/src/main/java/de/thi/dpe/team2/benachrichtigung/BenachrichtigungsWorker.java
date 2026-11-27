// Verantwortlich: Saifudin Mohammadi
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.benachrichtigung;

import io.quarkus.runtime.ShutdownEvent;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import java.util.HashMap;
import java.util.Map;
import org.camunda.bpm.client.ExternalTaskClient;
import org.camunda.bpm.client.task.ExternalTask;
import org.camunda.bpm.client.task.ExternalTaskService;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

/**
 * Holt die drei Benachrichtigungs-Topics von der Engine (CIB seven) ab und gibt sie an den Service weiter.
 * <ul>
 *   <li>t2-freigabeanfrage-senden (T2_Kundenentscheidung, "Freigabeanfrage senden")</li>
 *   <li>t2-lieferbestaetigung-anfordern (T2_Lieferpruefung, "Lieferbestätigung anfordern")</li>
 *   <li>t2-ergebnis-mitteilen (T2_Materialversorgung, "Ergebnis mitteilen" und alle Abbruch-Enden)</li>
 * </ul>
 * Fehler: Retries herunterzählen; bei 0 wird daraus ein Incident im Cockpit.
 */
@ApplicationScoped
public class BenachrichtigungsWorker {

    static final String TOPIC_FREIGABE = "t2-freigabeanfrage-senden";
    static final String TOPIC_LIEFERUNG = "t2-lieferbestaetigung-anfordern";
    static final String TOPIC_ERGEBNIS = "t2-ergebnis-mitteilen";

    private static final Logger LOG = Logger.getLogger(BenachrichtigungsWorker.class);

    @Inject
    BenachrichtigungsService service;

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
        client = ExternalTaskClient.create()
                .baseUrl(restUrl)
                .workerId(workerId)
                .asyncResponseTimeout(10_000)
                .build();

        client.subscribe(TOPIC_FREIGABE).lockDuration(lockDauer)
                .handler((task, ts) -> bearbeiten(task, ts,
                        () -> service.freigabeanfrageSenden(variablen(task), task.getProcessInstanceId())))
                .open();
        client.subscribe(TOPIC_LIEFERUNG).lockDuration(lockDauer)
                .handler((task, ts) -> bearbeiten(task, ts,
                        () -> service.lieferbestaetigungAnfordern(variablen(task), task.getProcessInstanceId())))
                .open();
        client.subscribe(TOPIC_ERGEBNIS).lockDuration(lockDauer)
                .handler((task, ts) -> bearbeiten(task, ts,
                        () -> service.ergebnisMitteilen(variablen(task), task.getActivityId(),
                                task.getProcessInstanceId())))
                .open();
        LOG.infof("Benachrichtigungs-Worker gestartet (%s), Topics: %s, %s, %s",
                restUrl, TOPIC_FREIGABE, TOPIC_LIEFERUNG, TOPIC_ERGEBNIS);
    }

    void stoppen(@Observes ShutdownEvent ev) {
        if (client != null) {
            client.stop();
        }
    }

    private void bearbeiten(ExternalTask task, ExternalTaskService ts, Runnable aktion) {
        try {
            aktion.run();
            ts.complete(task);
            LOG.infof("%s erledigt (Element %s, Instanz %s)", task.getTopicName(), task.getActivityId(),
                    task.getProcessInstanceId());
        } catch (RuntimeException e) {
            int rest = task.getRetries() == null ? wiederholungen : task.getRetries() - 1;
            LOG.errorf(e, "%s fehlgeschlagen, verbleibende Versuche: %d", task.getTopicName(), rest);
            ts.handleFailure(task, "Benachrichtigung fehlgeschlagen: " + e.getMessage(), e.toString(),
                    Math.max(rest, 0), 10_000L);
        }
    }

    private static Map<String, Object> variablen(ExternalTask task) {
        Map<String, Object> v = new HashMap<>(task.getAllVariables());
        if (task.getBusinessKey() != null) {
            v.putIfAbsent("businessKey", task.getBusinessKey());
            v.putIfAbsent("vorgangId", task.getBusinessKey());
        }
        return v;
    }
}
// KI-generiert (Claude, Anthropic) - Ende
