# XSD-Prüfung gegen das offizielle BPMN-2.0-Schema (OMG), wie es auch die Engine beim Deploy prüft.
import sys, glob
from lxml import etree
X='/usr/local/lib/python3.13/site-packages/SpiffWorkflow/bpmn/parser/schema/BPMN20.xsd'
schema=etree.XMLSchema(etree.parse(X))
ok=True
for f in sorted(glob.glob(sys.argv[1]+'/*.bpmn')):
    doc=etree.parse(f)
    if schema.validate(doc): print('XSD ok   ', f.split('/')[-1])
    else:
        ok=False; print('XSD FEHLER', f.split('/')[-1]); [print('   ',e) for e in schema.error_log]
sys.exit(0 if ok else 1)
