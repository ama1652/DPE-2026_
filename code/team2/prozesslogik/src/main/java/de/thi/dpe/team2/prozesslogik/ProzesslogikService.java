// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed)
// KI-generiert (Claude, Anthropic) - Beginn
package de.thi.dpe.team2.prozesslogik;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import de.thi.dpe.team2.prozesslogik.daten.Bestand;
import de.thi.dpe.team2.prozesslogik.daten.BestandRepository;
import de.thi.dpe.team2.prozesslogik.daten.Lieferant;
import de.thi.dpe.team2.prozesslogik.daten.LieferantRepository;
import de.thi.dpe.team2.prozesslogik.daten.Produkt;
import de.thi.dpe.team2.prozesslogik.daten.ProduktRepository;
import de.thi.dpe.team2.prozesslogik.daten.StammdatenRepository;
import de.thi.dpe.team2.prozesslogik.daten.Versorgungsprofil;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Fachlogik der Service-Aufgaben. Jede Methode bekommt die Prozessvariablen und gibt die neuen Variablen zurück.
 * Variablennamen = Namen im BPMN bzw. in den DMN-Tabellen.
 */
@ApplicationScoped
public class ProzesslogikService {

    @Inject
    EngineClient engine;
    @Inject
    StammdatenRepository profile;
    @Inject
    ProduktRepository produkte;
    @Inject
    LieferantRepository lieferanten;
    @Inject
    BestandRepository bestaende;
    @Inject
    ObjectMapper json;

    /** t2-vorgang-pruefen (Hauptprozess, Stiehl Punkt 2). */
    public Map<String, Object> vorgangPruefen(Map<String, Object> v) {
        String key = text(v, "businessKey");
        boolean offen = key != null && engine.laufendeVorgaenge(key) > 1;
        return Map.of("vorgangOffen", offen);
    }

    /** t2-reichweite-berechnen (Hauptprozess): Eingaben der DMN "Nachversorgungsbedarf" setzen. */
    @Transactional
    public Map<String, Object> reichweiteBerechnen(Map<String, Object> v) {
        Kennung k = kennung(v);
        Versorgungsprofil p = profile.profil(k.haushalt(), k.produkt())
                .orElseThrow(() -> new IllegalStateException("Kein Versorgungsprofil für " + k));
        List<Bestand> letzte = bestaende.letzte(k.haushalt(), p.produktId, 2);
        if (letzte.isEmpty()) {
            throw new IllegalStateException("Kein Bestand für " + k + " erfasst");
        }
        Bestand neu = letzte.get(0);
        Bestand alt = letzte.size() > 1 ? letzte.get(1) : null;
        Lieferant l = lieferant(p.produktId);
        double verbrauch = p.verbrauchProTag.doubleValue();

        Map<String, Object> aus = new HashMap<>();
        aus.put("pflegehaushaltId", k.haushalt());
        aus.put("produktId", p.produktId);
        aus.put("istBestand", neu.menge);
        aus.put("bestandMenge", neu.menge);
        aus.put("verbrauchProTag", verbrauch);
        aus.put("tageBisPruefung", p.pruefintervallTage);
        aus.put("lieferzeitTage", l.lieferzeitTage);
        aus.put("mindestbestand", p.mindestbestand);
        aus.put("zielbestand", p.zielbestand);
        aus.put("reichweiteTage", Rechner.reichweiteTage(neu.menge, verbrauch));
        aus.put("verbrauchssprung", Rechner.verbrauchssprung(verbrauch,
                alt == null ? null : alt.menge, alt == null ? null : alt.zeitpunkt, neu.menge, neu.zeitpunkt));
        return aus;
    }

    /** t2-vorschlag-erstellen (Bestellfreigabe): Vorschlag und Eingaben der DMN "Berechtigungsregel". */
    @Transactional
    public Map<String, Object> vorschlagErstellen(Map<String, Object> v) {
        Kennung k = kennung(v);
        Optional<Versorgungsprofil> gefunden = profile.profil(k.haushalt(), k.produkt());
        Map<String, Object> aus = new HashMap<>();
        if (gefunden.isEmpty()) {
            // Produkt nicht im Profil hinterlegt -> DMN führt zur Prüfstelle
            aus.put("produktHinterlegt", false);
            aus.put("produktGewechselt", false);
            aus.put("lieferantGewechselt", false);
            aus.put("preisGesamt", 0.0);
            aus.put("preisgrenze", 0.0);
            aus.put("bestellmenge", zahl(v, "nachversorgungsbedarf", 0));
            aus.put("zielbestand", 0);
            aus.put("freigabeHandlung", "Bestellung von " + k.produkt() + " (nicht im Versorgungsprofil)");
            aus.put("freigabeFolgen", "Ohne Freigabe wird nichts bestellt.");
            aus.put("bestellvorschlag", "{}");
            return aus;
        }
        Versorgungsprofil p = gefunden.get();
        boolean wiederholt = zahl(v, "anzahlVorschlaege", 0) > 0;
        boolean ersatz = (text(v, "ersatzGrund") != null || wiederholt) && p.ersatzProduktId != null;
        Produkt bevorzugt = produkt(p.produktId);
        Produkt gewaehlt = ersatz ? produkt(p.ersatzProduktId) : bevorzugt;
        int ist = istBestand(k.haushalt(), p.produktId);

        Rechner.Vorschlag vs = Rechner.vorschlag(gewaehlt.id, gewaehlt.name, gewaehlt.lieferantId,
                gewaehlt.packungsgroesse, gewaehlt.preisPackung, p.zielbestand, ist,
                bevorzugt.id, bevorzugt.lieferantId, true);

        aus.put("produktHinterlegt", vs.produktHinterlegt());
        aus.put("produktGewechselt", vs.produktGewechselt());
        aus.put("lieferantGewechselt", vs.lieferantGewechselt());
        aus.put("preisGesamt", vs.preisGesamt().doubleValue());
        aus.put("preisgrenze", p.preisgrenze.doubleValue());
        aus.put("bestellmenge", vs.stueck());
        aus.put("zielbestand", p.zielbestand);
        aus.put("bestellvorschlag", alsJson(vs, k.haushalt()));
        aus.put("freigabeHandlung", "Bestellung " + vs.packungen() + " Packung(en) " + vs.produktName()
                + " (" + vs.stueck() + " Stück) für " + vs.preisGesamt() + " EUR");
        aus.put("freigabeFolgen", "Ohne Freigabe wird nichts bestellt. Ihr Vorrat reicht noch ca. "
                + Rechner.reichweiteTage(ist, p.verbrauchProTag.doubleValue()) + " Tage.");
        return aus;
    }

    /** t2-ersatzoption-pruefen (Bestellabwicklung, Stiehl Punkt 7). */
    @Transactional
    public Map<String, Object> ersatzoptionPruefen(Map<String, Object> v) {
        Map<String, Object> vorschlag = ausJson(text(v, "bestellvorschlag"));
        String haushalt = text(v, "pflegehaushaltId");
        String produkt = (String) vorschlag.get("produktId");
        int versuche = zahl(v, "anzahlBestellversuche", 1);
        boolean moeglich = false;
        if (haushalt != null && produkt != null) {
            Optional<Versorgungsprofil> p = profile.profil(haushalt, produkt);
            if (p.isPresent() && p.get().ersatzProduktId != null && !p.get().ersatzProduktId.equals(produkt)) {
                boolean verfuegbar = produkte.findByIdOptional(p.get().ersatzProduktId).map(x -> x.verfuegbar)
                        .orElse(false);
                moeglich = Rechner.ersatzMoeglich(p.get().ersatzProduktId, verfuegbar, versuche);
            }
        }
        return Map.of("ersatzMoeglich", moeglich);
    }

    /** t2-bestand-fortschreiben (Hauptprozess, nach bestätigter Lieferung). */
    @Transactional
    public Map<String, Object> bestandFortschreiben(Map<String, Object> v) {
        Kennung k = kennung(v);
        Map<String, Object> vorschlag = ausJson(text(v, "bestellvorschlag"));
        int geliefert = vorschlag.get("stueck") instanceof Number n ? n.intValue() : 0;
        Versorgungsprofil p = profile.profil(k.haushalt(), k.produkt())
                .orElseThrow(() -> new IllegalStateException("Kein Versorgungsprofil für " + k));
        int neuerBestand = istBestand(k.haushalt(), p.produktId) + geliefert;

        Bestand b = new Bestand();
        b.pflegehaushaltId = k.haushalt();
        b.produktId = p.produktId;
        b.menge = neuerBestand;
        b.zeitpunkt = LocalDateTime.now();
        b.herkunft = "Fortschreibung";
        bestaende.persist(b);
        return Map.of("istBestand", neuerBestand,
                "reichweiteTage", Rechner.reichweiteTage(neuerBestand, p.verbrauchProTag.doubleValue()));
    }

    // ------------------------------------------------------------------ Hilfen

    record Kennung(String haushalt, String produkt) {
    }

    /** Haushalt und Produkt aus den Variablen oder aus dem Business Key PH-0001:TP-M. */
    static Kennung kennung(Map<String, Object> v) {
        String haushalt = text(v, "pflegehaushaltId");
        String produkt = text(v, "produktId");
        String key = text(v, "businessKey");
        if ((haushalt == null || produkt == null) && key != null && key.contains(":")) {
            String[] teile = key.split(":", 2);
            haushalt = haushalt == null ? teile[0] : haushalt;
            produkt = produkt == null ? teile[1] : produkt;
        }
        if (haushalt == null || produkt == null) {
            throw new IllegalArgumentException("pflegehaushaltId/produktId fehlen (Business Key PH-xxxx:Produkt)");
        }
        return new Kennung(haushalt, produkt);
    }

    private int istBestand(String haushalt, String produkt) {
        List<Bestand> letzte = bestaende.letzte(haushalt, produkt, 1);
        return letzte.isEmpty() ? 0 : letzte.get(0).menge;
    }

    private Produkt produkt(String id) {
        return produkte.findByIdOptional(id).orElseThrow(() -> new IllegalStateException("Produkt fehlt: " + id));
    }

    private Lieferant lieferant(String produktId) {
        String id = produkt(produktId).lieferantId;
        return lieferanten.findByIdOptional(id).orElseThrow(() -> new IllegalStateException("Lieferant fehlt: " + id));
    }

    private String alsJson(Rechner.Vorschlag vs, String haushalt) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("pflegehaushaltId", haushalt);
        m.put("produktId", vs.produktId());
        m.put("produktName", vs.produktName());
        m.put("lieferantId", vs.lieferantId());
        m.put("packungen", vs.packungen());
        m.put("stueck", vs.stueck());
        m.put("preisGesamt", vs.preisGesamt());
        try {
            return json.writeValueAsString(m);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException(e);
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> ausJson(String s) {
        if (s == null || s.isBlank()) {
            return Map.of();
        }
        try {
            return json.readValue(s, Map.class);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("bestellvorschlag ist kein JSON: " + s, e);
        }
    }

    static String text(Map<String, Object> v, String name) {
        Object o = v.get(name);
        return (o == null || o.toString().isBlank()) ? null : o.toString();
    }

    static int zahl(Map<String, Object> v, String name, int ersatz) {
        Object o = v.get(name);
        if (o instanceof Number n) {
            return n.intValue();
        }
        try {
            return o == null ? ersatz : Integer.parseInt(o.toString());
        } catch (NumberFormatException e) {
            return ersatz;
        }
    }
}
// KI-generiert (Claude, Anthropic) - Ende
