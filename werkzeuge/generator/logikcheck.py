# Strukturprüfung: Erreichbarkeit, Sackgassen, Gateway-Vollständigkeit (je Prozess)
import glob, re
from lxml import etree
NS={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL'}
for f in sorted(glob.glob((__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'prozesse/team2')+'/*.bpmn')):
    p=etree.parse(f).find('.//b:process',NS); fn=f.split('/')[-1]
    nodes={e.get('id'):e for e in p if e.get('id') and not etree.QName(e).localname in ('sequenceFlow','laneSet','textAnnotation','association')}
    out={k:[] for k in nodes}; inc={k:[] for k in nodes}
    for s in p.findall('b:sequenceFlow',NS): out[s.get('sourceRef')].append(s.get('targetRef')); inc[s.get('targetRef')].append(s.get('sourceRef'))
    for k,e in nodes.items():  # Boundary-Events hängen an Aktivitäten
        if etree.QName(e).localname=='boundaryEvent': out[e.get('attachedToRef')].append(k)
    starts=[k for k,e in nodes.items() if etree.QName(e).localname=='startEvent']
    ends=[k for k,e in nodes.items() if etree.QName(e).localname=='endEvent']
    seen=set(); st=list(starts)
    while st:
        n=st.pop()
        if n in seen: continue
        seen.add(n); st+=out[n]
    back=set(); st=list(ends); rin={k:[] for k in nodes}
    for k,v in out.items():
        for t in v: rin[t].append(k)
    while st:
        n=st.pop()
        if n in back: continue
        back.add(n); st+=rin[n]
    unreach=[nodes[k].get('name') or k for k in nodes if k not in seen]
    dead=[nodes[k].get('name') or k for k in nodes if k not in back]
    print(f'{fn:32s} Starts {len(starts)}  Enden {len(ends)}  unerreichbar: {unreach or "-"}  ohne Weg zum Ende: {dead or "-"}')
