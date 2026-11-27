// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import org.eclipse.microprofile.config.inject.ConfigProperty;

/** Kleiner Lesezugriff auf die REST-API von CIB seven (nur was "Laufenden Vorgang prüfen" braucht). */
@ApplicationScoped
public class EngineClient {

    static final String HAUPTPROZESS = "T2_Materialversorgung";

    @ConfigProperty(name = "team2.engine.rest-url")
    String restUrl;

    @Inject
    ObjectMapper json;

    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();

    /** Anzahl laufender Instanzen des Hauptprozesses mit diesem Business Key (die eigene Instanz zählt mit). */
    public long laufendeVorgaenge(String businessKey) {
        String url = restUrl + "/process-instance/count?processDefinitionKey=" + HAUPTPROZESS
                + "&businessKey=" + URLEncoder.encode(businessKey, StandardCharsets.UTF_8);
        try {
            HttpResponse<String> antwort = http.send(HttpRequest.newBuilder(URI.create(url)).GET().build(),
                    HttpResponse.BodyHandlers.ofString());
            if (antwort.statusCode() != 200) {
                throw new IllegalStateException("Engine antwortet mit " + antwort.statusCode() + ": " + antwort.body());
            }
            JsonNode knoten = json.readTree(antwort.body());
            return knoten.path("count").asLong();
        } catch (IOException e) {
            throw new IllegalStateException("Engine nicht erreichbar: " + e.getMessage(), e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Abfrage unterbrochen", e);
        }
    }
}
// KI-generiert (Claude, Anthropic) - Ende
