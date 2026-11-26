# BPMN-Generator Team 2

> **KI-Kennzeichnung:** Erstellt mit Claude (Anthropic). Verantwortlich: Saifudin Mohammadi.

Erzeugt die 5 BPMN-Dateien aus Python (Positionen, Labels, Camunda-Attribute) und prüft sie.

```bash
pip install lxml SpiffWorkflow   # SpiffWorkflow bringt das BPMN-2.0-XSD mit
python3 werkzeuge/generator/modelle.py prozesse/team2      # Modelle neu erzeugen
python3 werkzeuge/generator/xsdcheck.py prozesse/team2     # gegen das BPMN-2.0-XSD (Pfad in xsdcheck.py ggf. anpassen)
python3 werkzeuge/stilcheck.py prozesse/team2              # Stilregeln, Label-Matching, DMN-Verweise
python3 werkzeuge/generator/logikcheck.py prozesse/team2   # Erreichbarkeit aller Enden
```
Bilder: im Camunda Modeler exportieren oder mit bpmn-to-image rendern.
