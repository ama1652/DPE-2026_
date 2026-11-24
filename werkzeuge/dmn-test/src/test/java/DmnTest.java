// KI-generiert (Claude, Anthropic). Team 2: deployt alle BPMN- und DMN-Dateien in eine Camunda-7-Engine im Speicher und prüft beide Entscheidungstabellen und die Regelaufgaben im Prozess. Start: cd werkzeuge/dmn-test && mvn test
import org.camunda.bpm.engine.*;
import org.camunda.bpm.engine.externaltask.LockedExternalTask;
import org.camunda.bpm.engine.impl.cfg.StandaloneInMemProcessEngineConfiguration;
import org.camunda.bpm.engine.runtime.ProcessInstance;
import org.camunda.bpm.engine.variable.VariableMap;
import org.camunda.bpm.engine.variable.Variables;
import org.junit.jupiter.api.*;
import java.nio.file.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class DmnTest {
  ProcessEngine engine; RuntimeService rt; DecisionService ds;
  static final Path DIR = Paths.get(System.getProperty("modelDir", "../../prozesse/team2"));

  @BeforeAll void setup() throws Exception {
    StandaloneInMemProcessEngineConfiguration c = new StandaloneInMemProcessEngineConfiguration();
    c.setJdbcUrl("jdbc:h2:mem:t;DB_CLOSE_DELAY=-1"); c.setHistory("full");
    engine = c.buildProcessEngine(); rt = engine.getRuntimeService(); ds = engine.getDecisionService();
    var d = engine.getRepositoryService().createDeployment().name("team2");
    try (var s = Files.list(DIR)) { for (Path p : s.filter(p -> p.toString().matches(".*\\.(bpmn|dmn)$")).toList())
      d.addInputStream(p.getFileName().toString(), Files.newInputStream(p)); }
    d.deploy();
    System.out.println("Deployt: " + engine.getRepositoryService().createProcessDefinitionQuery().count() + " Prozesse, "
      + engine.getRepositoryService().createDecisionDefinitionQuery().count() + " Entscheidungen");
  }

  Map<String,Object> bedarf(double ist, double vpt, int tage, int liefer, double min, double ziel) {
    return ds.evaluateDecisionByKey("Nachversorgungsbedarf").variables(Variables.createVariables()
      .putValue("istBestand", ist).putValue("verbrauchProTag", vpt).putValue("tageBisPruefung", tage)
      .putValue("lieferzeitTage", liefer).putValue("mindestbestand", min).putValue("zielbestand", ziel)).evaluate().getSingleResult().getEntryMap();
  }
  VariableMap ok() { return Variables.createVariables().putValue("produktHinterlegt", true).putValue("produktGewechselt", false)
      .putValue("lieferantGewechselt", false).putValue("verbrauchssprung", false).putValue("preisGesamt", 40.0)
      .putValue("preisgrenze", 50.0).putValue("bestellmenge", 90).putValue("zielbestand", 100); }
  String weg(VariableMap v) {
    var r = ds.evaluateDecisionByKey("Berechtigungsregel").variables(v).evaluate().getSingleResult();
    System.out.println("  Berechtigungsregel " + v + " -> " + r.getEntryMap()); return (String) r.getEntry("freigabeweg");
  }

  @Test void nachversorgungsbedarf() {
    // 100 Stück, 4/Tag, 10 Tage Prüfintervall + 3 Tage Lieferzeit -> 48 übrig; Mindestbestand 30 -> reicht
    var a = bedarf(100, 4, 10, 3, 30, 120); System.out.println("  Bedarf reicht: " + a);
    assertEquals(false, a.get("nachversorgungErforderlich")); assertEquals(0, ((Number)a.get("nachversorgungsbedarf")).intValue());
    // 60 Stück -> 8 übrig < 30 -> nachversorgen, Bedarf 120-60 = 60
    var b = bedarf(60, 4, 10, 3, 30, 120); System.out.println("  Bedarf nötig: " + b);
    assertEquals(true, b.get("nachversorgungErforderlich")); assertEquals(60, ((Number)b.get("nachversorgungsbedarf")).intValue());
    // Grenzfall: genau Mindestbestand -> reicht
    assertEquals(false, bedarf(82, 4, 10, 3, 30, 120).get("nachversorgungErforderlich"));
  }

  @Test void berechtigungsregel() {
    assertEquals("AUTOMATISCH", weg(ok()));
    assertEquals("KUNDENFREIGABE", weg(ok().putValue("preisGesamt", 55.0)));
    assertEquals("AUTOMATISCH", weg(ok().putValue("preisGesamt", 50.0)));
    assertEquals("KUNDENFREIGABE", weg(ok().putValue("produktGewechselt", true)));
    assertEquals("KUNDENFREIGABE", weg(ok().putValue("lieferantGewechselt", true)));
    assertEquals("KUNDENFREIGABE", weg(ok().putValue("bestellmenge", 120)));
    assertEquals("PRUEFUNG", weg(ok().putValue("verbrauchssprung", true)));
    assertEquals("PRUEFUNG", weg(ok().putValue("produktHinterlegt", false)));
    // strengster Weg gewinnt
    assertEquals("PRUEFUNG", weg(ok().putValue("preisGesamt", 99.0).putValue("verbrauchssprung", true)));
    // fehlende Daten -> keine Regel greift (Prozess bekäme einen Incident), nie AUTOMATISCH
    var fehlt = ok(); fehlt.remove("preisGesamt");
    assertNull(ds.evaluateDecisionByKey("Berechtigungsregel").variables(fehlt).evaluate().getSingleResult());
  }

  ProcessInstance startBedarf(double ist, boolean sprung) {
    return rt.createProcessInstanceByKey("T2_Materialversorgung").businessKey("PH-1:" + ist)
      .startBeforeActivity("SB_Bedarf").setVariables(Variables.createVariables()
        .putValue("istBestand", ist).putValue("verbrauchProTag", 4).putValue("tageBisPruefung", 10).putValue("lieferzeitTage", 3)
        .putValue("mindestbestand", 30).putValue("zielbestand", 120).putValue("verbrauchssprung", sprung)
        .putValue("anzahlBestellversuche", 0).putValue("ersatzGrund", null)).execute();
  }
  void vorschlagErledigen(VariableMap v) {
    List<LockedExternalTask> l = engine.getExternalTaskService().fetchAndLock(1, "test").topic("t2-vorschlag-erstellen", 10000).execute();
    assertEquals(1, l.size(), "Worker-Aufgabe 'Produkt und Menge vorschlagen' sollte warten");
    v.remove("verbrauchssprung"); // kommt aus dem Hauptprozess
    engine.getExternalTaskService().complete(l.get(0).getId(), "test", v);
  }
  List<String> aktiv() { return engine.getHistoryService().createHistoricActivityInstanceQuery().unfinished().list()
      .stream().map(a -> a.getActivityId()).toList(); }
  Object histVar(String pi, String name) { var v = engine.getHistoryService().createHistoricVariableInstanceQuery()
      .processInstanceId(pi).variableName(name).singleResult(); return v == null ? null : v.getValue(); }

  @Test void prozess_bestandReicht() {
    var pi = startBedarf(100, false);
    assertTrue(engine.getHistoryService().createHistoricProcessInstanceQuery().processInstanceId(pi.getId()).singleResult().getEndActivityId().equals("End_Ausreichend"));
    assertEquals(false, histVar(pi.getId(), "nachversorgungErforderlich"));
    System.out.println("  Prozess: Bestand reicht -> End_Ausreichend, Grund: " + histVar(pi.getId(), "bedarfsbegruendung"));
  }

  @Test void prozess_automatisch() {
    cleanup(); var pi = startBedarf(60, false);
    assertEquals(60, ((Number) histVar(pi.getId(), "nachversorgungsbedarf")).intValue());
    vorschlagErledigen(ok());
    var a = aktiv(); System.out.println("  Prozess automatisch -> aktiv: " + a);
    assertTrue(a.contains("CA_Bestellabwicklung"), "Nach automatischer Freigabe sollte die Bestellabwicklung laufen");
  }

  @Test void prozess_kundenfreigabe() {
    cleanup(); startBedarf(60, false); vorschlagErledigen(ok().putValue("preisGesamt", 70.0));
    var a = aktiv(); System.out.println("  Prozess Preis zu hoch -> aktiv: " + a);
    assertTrue(a.contains("CA_KE"), "Kundenentscheidung sollte laufen");
  }

  @Test void prozess_pruefung() {
    cleanup(); startBedarf(60, true); vorschlagErledigen(ok());
    var t = engine.getTaskService().createTaskQuery().taskDefinitionKey("UT_Grenzfall").singleResult();
    assertNotNull(t, "Prüfstelle sollte 'Grenzfall prüfen' bekommen");
    Object grund = engine.getTaskService().getVariable(t.getId(), "freigabeBegruendung");
    System.out.println("  Prozess Verbrauchssprung -> Benutzeraufgabe " + t.getName() + ", Begründung: " + grund);
    assertEquals("Verbrauch deutlich verändert", grund);
  }

  void cleanup() { rt.createProcessInstanceQuery().list().forEach(p -> { try { rt.deleteProcessInstance(p.getId(), "t"); } catch (Exception e) {} });
    engine.getTaskService().createTaskQuery().list(); }
}
