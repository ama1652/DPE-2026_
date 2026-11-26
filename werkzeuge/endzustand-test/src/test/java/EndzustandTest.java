// Verantwortlich: Saifudin Mohammadi (übernommen von Mohammed, Story T2-06)
// KI-generiert (Claude, Anthropic) - Beginn
// Deployt alle BPMN- und DMN-Dateien von Team 2 in eine Camunda-7-Engine im Speicher (gleiche Engine wie CIB seven)
// und spielt jeden Endzustand des Hauptprozesses einmal durch. Die Worker werden simuliert: Der Test holt jede
// External Task ab und schließt sie mit den Variablen des Testfalls ab (Testfälle: testdaten/team2).
// Start: cd werkzeuge/endzustand-test && mvn test
import org.camunda.bpm.engine.*;
import org.camunda.bpm.engine.externaltask.ExternalTask;
import org.camunda.bpm.engine.externaltask.LockedExternalTask;
import org.camunda.bpm.engine.impl.cfg.StandaloneInMemProcessEngineConfiguration;
import org.camunda.bpm.engine.runtime.EventSubscription;
import org.camunda.bpm.engine.runtime.Job;
import org.camunda.bpm.engine.task.Task;
import org.junit.jupiter.api.*;
import java.nio.file.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class EndzustandTest {
  static final Path DIR = Paths.get(System.getProperty("modelDir", "../../prozesse/team2"));
  static final Object TIMEOUT = "TIMEOUT";
  ProcessEngine engine; RuntimeService rt; ExternalTaskService ext; TaskService tasks; ManagementService mgmt; HistoryService hist;
  int nr = 0;

  @BeforeAll void deployen() throws Exception {
    StandaloneInMemProcessEngineConfiguration c = new StandaloneInMemProcessEngineConfiguration();
    c.setJdbcUrl("jdbc:h2:mem:endzustand;DB_CLOSE_DELAY=-1"); c.setHistory("full"); c.setJobExecutorActivate(false);
    engine = c.buildProcessEngine();
    rt = engine.getRuntimeService(); ext = engine.getExternalTaskService(); tasks = engine.getTaskService();
    mgmt = engine.getManagementService(); hist = engine.getHistoryService();
    var d = engine.getRepositoryService().createDeployment().name("team2");
    try (var s = Files.list(DIR)) { for (Path p : s.filter(p -> p.toString().matches(".*\\.(bpmn|dmn)$")).toList())
      d.addInputStream(p.getFileName().toString(), Files.newInputStream(p)); }
    d.deploy();
    assertEquals(5, engine.getRepositoryService().createProcessDefinitionQuery().count(), "5 Prozesse deployt");
    assertEquals(2, engine.getRepositoryService().createDecisionDefinitionQuery().count(), "2 DMN deployt");
  }

  @AfterAll void stoppen() { engine.close(); }

  /** Ein Testfall: Variablen je Topic (überschreiben die Standardwerte) und Antworten je Nachricht der Reihe nach. */
  class Fall {
    final Map<String, Map<String, Object>> topic = new HashMap<>();
    final Map<String, Deque<Object>> antwort = new HashMap<>();
    final Deque<String> pruefung = new ArrayDeque<>();
    Fall() {
      topic.put("t2-vorgang-pruefen", Map.of("vorgangOffen", false));
      topic.put("t2-reichweite-berechnen", new HashMap<>(Map.of("istBestand", 30, "bestandMenge", 30, "verbrauchProTag", 4.0,
          "tageBisPruefung", 10, "lieferzeitTage", 3, "mindestbestand", 40, "zielbestand", 120, "verbrauchssprung", false)));
      topic.put("t2-vorschlag-erstellen", new HashMap<>(Map.of("produktHinterlegt", true, "produktGewechselt", false,
          "lieferantGewechselt", false, "preisGesamt", 74.70, "preisgrenze", 75.0, "bestellmenge", 90, "zielbestand", 120,
          "bestellvorschlag", "{\"produktId\":\"TP-M\",\"stueck\":90}", "freigabeHandlung", "3 Packungen Testprodukt M",
          "freigabeFolgen", "Vorrat reicht ca. 7 Tage")));
      topic.put("t2-ersatzoption-pruefen", Map.of("ersatzMoeglich", false));
    }
    Fall setze(String t, String name, Object wert) { topic.computeIfAbsent(t, k -> new HashMap<>());
      Map<String, Object> m = new HashMap<>(topic.get(t)); m.put(name, wert); topic.put(t, m); return this; }
    Fall antworte(String nachricht, Object... folge) { antwort.computeIfAbsent(nachricht, k -> new ArrayDeque<>()).addAll(Arrays.asList(folge)); return this; }
    Fall pruefe(String ergebnis) { pruefung.add(ergebnis); return this; }
  }
  static Map<String, Object> v(Object... kv) { Map<String, Object> m = new HashMap<>(); for (int i = 0; i < kv.length; i += 2) m.put((String) kv[i], kv[i + 1]); return m; }

  static final String KUNDE = "PflegeApp_Kundenentscheidung_Team2", LIEF_ANTWORT = "Lieferant_Bestellantwort_Team2",
      VERSAND = "Lieferant_Versandmeldung_Team2", BESTAETIGUNG = "PflegeApp_Lieferbestaetigung_Team2",
      KLAERUNG = "Team3_Klaerungsergebnis_Team2";

  /** Spielt den Fall durch und gibt die ID der Hauptinstanz zurück. */
  String spielen(Fall f) {
    String key = "PH-0001:TP-M-" + (++nr);
    String pi = rt.startProcessInstanceByMessage("PflegeApp_Bestandsmeldung_Team2", key,
        v("pflegehaushaltId", "PH-0001", "produktId", "TP-M")).getId();
    for (int schritt = 0; schritt < 300; schritt++) {
      if (hist.createHistoricProcessInstanceQuery().processInstanceId(pi).finished().count() == 1) return pi;
      List<ExternalTask> offen = ext.createExternalTaskQuery().notLocked().active().list();
      if (!offen.isEmpty()) {
        String t = offen.get(0).getTopicName();
        List<LockedExternalTask> l = ext.fetchAndLock(1, "test").topic(t, 60_000).execute();
        ext.complete(l.get(0).getId(), "test", f.topic.getOrDefault(t, Map.of()));
        continue;
      }
      Task ut = tasks.createTaskQuery().active().list().stream().findFirst().orElse(null);
      if (ut != null) { tasks.complete(ut.getId(), v("pruefergebnis", f.pruefung.pop(), "pruefbegruendung", "Test")); continue; }
      List<EventSubscription> subs = rt.createEventSubscriptionQuery().eventType("message").list().stream()
          .filter(e -> e.getExecutionId() != null).toList();
      if (!subs.isEmpty()) {
        EventSubscription e = subs.get(0);
        Deque<Object> folge = f.antwort.get(e.getEventName());
        assertNotNull(folge, "Keine Antwort im Testfall für " + e.getEventName());
        Object a = folge.isEmpty() ? TIMEOUT : folge.pop();
        if (a == TIMEOUT) {
          List<Job> timer = mgmt.createJobQuery().processInstanceId(e.getProcessInstanceId()).timers().list();
          assertEquals(1, timer.size(), "genau ein Timer an " + e.getActivityId());
          mgmt.executeJob(timer.get(0).getId());
        } else {
          @SuppressWarnings("unchecked") Map<String, Object> werte = (Map<String, Object>) a;
          rt.createMessageCorrelation(e.getEventName()).processInstanceId(e.getProcessInstanceId()).setVariables(werte).correlate();
        }
        continue;
      }
      fail("Prozess hängt: keine Aufgabe, keine Nachricht offen (Instanz " + pi + ")");
    }
    fail("mehr als 300 Schritte");
    return pi;
  }

  void endetIn(String pi, String ende) {
    assertEquals(1, hist.createHistoricActivityInstanceQuery().processInstanceId(pi).activityId(ende).finished().count(),
        "Hauptprozess endet in " + ende);
    System.out.println("OK  " + ende);
  }

  Fall lieferungOk(Fall f) {
    return f.antworte(LIEF_ANTWORT, v("bestellantwortStatus", "BESTAETIGT")).antworte(VERSAND, v())
        .antworte(BESTAETIGUNG, v("lieferbefund", "RICHTIG"));
  }

  @Test void tf01_nachversorgungAbgeschlossen() { endetIn(spielen(lieferungOk(new Fall())), "End_Abgeschlossen"); }

  @Test void tf02_bestandAusreichend() {
    endetIn(spielen(new Fall().setze("t2-reichweite-berechnen", "istBestand", 110)), "End_Ausreichend"); }

  @Test void tf03_vorgangBereitsOffen() {
    endetIn(spielen(new Fall().setze("t2-vorgang-pruefen", "vorgangOffen", true)), "End_Offen"); }

  @Test void tf04_preisZuHoch_kundeGibtFrei() {
    endetIn(spielen(lieferungOk(new Fall().setze("t2-vorschlag-erstellen", "preisGesamt", 82.5)
        .antworte(KUNDE, v("entscheidung", "FREIGEBEN"))))), "End_Abgeschlossen"); }

  @Test void tf05_kundeLehntAb() {
    endetIn(spielen(new Fall().setze("t2-vorschlag-erstellen", "preisGesamt", 82.5)
        .antworte(KUNDE, v("entscheidung", "ABLEHNEN"))), "End_NichtFreigegeben"); }

  @Test void tf06_kundeSchiebtAuf() {
    endetIn(spielen(new Fall().setze("t2-vorschlag-erstellen", "preisGesamt", 82.5)
        .antworte(KUNDE, v("entscheidung", "AUFSCHIEBEN"))), "End_Aufgeschoben"); }

  @Test void tf07_keineAntwortTrotzNachfassen() {
    endetIn(spielen(new Fall().setze("t2-vorschlag-erstellen", "preisGesamt", 82.5)
        .antworte(KUNDE, TIMEOUT, TIMEOUT)), "End_NichtFreigegeben"); }

  @Test void tf08_dreimalAenderung_keineEinigung() {
    endetIn(spielen(new Fall().setze("t2-vorschlag-erstellen", "preisGesamt", 82.5)
        .antworte(KUNDE, v("entscheidung", "AENDERN"), v("entscheidung", "AENDERN"), v("entscheidung", "AENDERN"))),
        "End_NichtFreigegeben"); }

  @Test void tf09_pruefstelle_nichtZulaessig() {
    endetIn(spielen(new Fall().setze("t2-vorschlag-erstellen", "produktHinterlegt", false).pruefe("NICHT_ZULAESSIG")),
        "End_NichtZulaessig"); }

  @Test void tf10_verbrauchssprung_pruefstelleHoltFreigabe() {
    endetIn(spielen(lieferungOk(new Fall().setze("t2-reichweite-berechnen", "verbrauchssprung", true)
        .pruefe("KUNDENFREIGABE").antworte(KUNDE, v("entscheidung", "FREIGEBEN")))), "End_Abgeschlossen"); }

  @Test void tf11_ersatzSchleife() {
    Fall f = new Fall().setze("t2-ersatzoption-pruefen", "ersatzMoeglich", true)
        .antworte(LIEF_ANTWORT, v("bestellantwortStatus", "NICHT_VERFUEGBAR"), v("bestellantwortStatus", "BESTAETIGT"))
        .antworte(VERSAND, v()).antworte(BESTAETIGUNG, v("lieferbefund", "RICHTIG"));
    endetIn(spielen(f), "End_Abgeschlossen"); }

  @Test void tf12_nichtVerfuegbar_keinErsatz() {
    endetIn(spielen(new Fall().antworte(LIEF_ANTWORT, v("bestellantwortStatus", "NICHT_VERFUEGBAR"))), "End_KeineBestellung"); }

  @Test void tf13_lieferantAntwortetNicht() {
    endetIn(spielen(new Fall().antworte(LIEF_ANTWORT, TIMEOUT, TIMEOUT)), "End_KeineBestellung"); }

  @Test void tf14_teillieferung_nachlieferungBestaetigt() {
    endetIn(spielen(new Fall().antworte(LIEF_ANTWORT, v("bestellantwortStatus", "BESTAETIGT")).antworte(VERSAND, v())
        .antworte(BESTAETIGUNG, v("lieferbefund", "TEILWEISE"))
        .antworte(KLAERUNG, v("klaerungsergebnis", "NACHLIEFERUNG_BESTAETIGT"))), "End_Abgeschlossen"); }

  @Test void tf15_falschlieferung_ungeklaert() {
    endetIn(spielen(new Fall().antworte(LIEF_ANTWORT, v("bestellantwortStatus", "BESTAETIGT")).antworte(VERSAND, v())
        .antworte(BESTAETIGUNG, v("lieferbefund", "FALSCH"))
        .antworte(KLAERUNG, v("klaerungsergebnis", "NICHT_GEKLAERT"))), "End_Ungeklaert"); }

  @Test void tf16_lieferungUnbestaetigt() {
    endetIn(spielen(new Fall().antworte(LIEF_ANTWORT, v("bestellantwortStatus", "BESTAETIGT")).antworte(VERSAND, v())
        .antworte(BESTAETIGUNG, TIMEOUT).antworte(KLAERUNG, TIMEOUT)), "End_Ungeklaert"); }
}
// KI-generiert (Claude, Anthropic) - Ende
