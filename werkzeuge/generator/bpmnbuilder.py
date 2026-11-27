"""Kleiner BPMN-2.0-Generator (Camunda 7 / CIB seven) mit Diagramm-Koordinaten.
Verantwortlich: Saifudin Mohammadi.

Hilfswerkzeug für Team 2, nicht Teil der Abgabe.
Ziel: XSD-konforme Elementreihenfolge, saubere DI (Layout) und Camunda-Erweiterungen.
"""
from xml.sax.saxutils import escape, quoteattr

SIZES = {
    'task': (140, 80), 'call': (140, 80),
    'event': (36, 36), 'gateway': (50, 50),
}
TASK_KINDS = {'serviceTask', 'sendTask', 'receiveTask', 'userTask', 'businessRuleTask', 'callActivity', 'task', 'subProcess'}
EVENT_KINDS = {'startEvent', 'endEvent', 'intermediateCatchEvent', 'intermediateThrowEvent', 'boundaryEvent'}
GW_KINDS = {'exclusiveGateway', 'eventBasedGateway', 'parallelGateway'}


def a(v):
    return quoteattr(str(v))


class Node:
    def __init__(self, id, kind, name, cx, cy, **kw):
        self.id, self.kind, self.name, self.cx, self.cy = id, kind, name, cx, cy
        self.kw = kw
        if kind in TASK_KINDS:
            self.w, self.h = kw.get('size', SIZES['task'])
        elif kind in EVENT_KINDS:
            self.w, self.h = SIZES['event']
        else:
            self.w, self.h = SIZES['gateway']
        self.incoming, self.outgoing = [], []
        self.boundaries = []

    def anchor(self, side, offset=0):
        if side == 'left':
            return (self.cx - self.w / 2, self.cy + offset)
        if side == 'right':
            return (self.cx + self.w / 2, self.cy + offset)
        if side == 'top':
            return (self.cx + offset, self.cy - self.h / 2)
        if side == 'bottom':
            return (self.cx + offset, self.cy + self.h / 2)
        raise ValueError(side)

    def label_bounds(self):
        """Beschriftung für Ereignisse/Gateways (extern)."""
        pos = self.kw.get('label', 'bottom')
        w = self.kw.get('label_w', 100)
        lines = max(1, (len(self.name) * 6 + w - 1) // w)
        h = 14 * lines
        if isinstance(pos, tuple):
            return pos[0], pos[1], w, h
        if pos == 'bottom':
            return self.cx - w / 2, self.cy + self.h / 2 + 4, w, h
        if pos == 'top':
            return self.cx - w / 2, self.cy - self.h / 2 - 4 - h, w, h
        if pos == 'right':
            w = min(110, max(w, len(self.name) * 6))
            lines = max(1, (len(self.name) * 6 + w - 1) // w)
            h = 14 * lines
            return self.cx + self.w / 2 + 6, self.cy - h / 2, w, h
        if pos == 'left':
            return self.cx - self.w / 2 - 6 - w, self.cy - h / 2, w, h
        if pos == 'topleft':
            return self.cx - self.w / 2 - w + 10, self.cy - self.h / 2 - h - 2, w, h
        if pos == 'topright':
            return self.cx + self.w / 2 - 10, self.cy - self.h / 2 - h - 2, w, h
        if pos == 'bottomright':
            return self.cx + self.w / 2 - 6, self.cy + self.h / 2 - 2, w, h
        raise ValueError(pos)


class Flow:
    def __init__(self, id, src, tgt, name=None, cond=None, waypoints=None, label=None, listeners=None, default=False):
        self.id, self.src, self.tgt, self.name, self.cond = id, src, tgt, name, cond
        self.waypoints, self.label, self.listeners, self.default = waypoints, label, listeners or [], default


class Process:
    def __init__(self, id, name, doc=None, executable=True):
        self.id, self.name, self.doc, self.executable = id, name, doc, executable
        self.nodes, self.flows, self.lanes = {}, [], []
        self.order = []
        self.annotations, self.assocs = [], []   # (id, text, x, y, w, h) / (id, src, tgt, waypoints)

    def annotate(self, id, text, x, y, w, h, src, waypoints):
        self.annotations.append((id, text, x, y, w, h))
        self.assocs.append((id + '_Assoc', src, id, waypoints))

    def add(self, id, kind, name, cx, cy, **kw):
        n = Node(id, kind, name, cx, cy, **kw)
        self.nodes[id] = n
        self.order.append(id)
        if kind == 'boundaryEvent':
            self.nodes[kw['attached']].boundaries.append(id)
        return n

    def flow(self, id, src, tgt, src_side='right', tgt_side='left', via=None, name=None, cond=None,
             label=None, listeners=None, src_off=0, tgt_off=0, default=False, start_pt=None):
        s, t = self.nodes[src], self.nodes[tgt]
        p1, p2 = s.anchor(src_side, src_off), t.anchor(tgt_side, tgt_off)
        if start_pt:
            p1 = start_pt
        pts = [p1]
        if via:
            pts += via
        else:
            h1, h2 = src_side in ('left', 'right'), tgt_side in ('left', 'right')
            if p1[0] == p2[0] or p1[1] == p2[1]:
                pass
            elif h1 and not h2:
                pts.append((p2[0], p1[1]))
            elif not h1 and h2:
                pts.append((p1[0], p2[1]))
            elif h1 and h2:
                mx = (p1[0] + p2[0]) / 2
                pts += [(mx, p1[1]), (mx, p2[1])]
            else:
                my = (p1[1] + p2[1]) / 2
                pts += [(p1[0], my), (p2[0], my)]
        pts.append(p2)
        f = Flow(id, src, tgt, name, cond, pts, label, listeners, default)
        self.flows.append(f)
        s.outgoing.append(id)
        t.incoming.append(id)
        return f


class Collab:
    def __init__(self, id):
        self.id = id
        self.participants = []   # (id, name, processRef or None, x, y, w, h)
        self.msgflows = []       # (id, name, src, tgt, waypoints, label)

    def participant(self, id, name, x, y, w, h, process=None):
        self.participants.append((id, name, process, x, y, w, h))

    def msg(self, id, name, src, tgt, waypoints, label=None):
        self.msgflows.append((id, name, src, tgt, waypoints, label))


def flow_label_bounds(f):
    if f.label:
        x, y = f.label[0], f.label[1]
        w = f.label[2] if len(f.label) > 2 else 90
    else:
        (x1, y1), (x2, y2) = f.waypoints[0], f.waypoints[1]
        w = 90
        if x1 == x2:  # vertikal
            x, y = x1 + 6, (y1 + y2) / 2 - 7 if abs(y2 - y1) < 60 else min(y1, y2) + 8
        else:
            x, y = min(x1, x2) + 6, y1 - 30
    lines = max(1, (len(f.name) * 6 + w - 1) // w)
    return x, y, w, 14 * lines


def ext_block(items):
    return ('<bpmn:extensionElements>' + ''.join(items) + '</bpmn:extensionElements>') if items else ''


def listener(expr, event='start'):
    return f'<camunda:executionListener expression={a(expr)} event="{event}" />'


def doc_el(text):
    return f'<bpmn:documentation>{escape(text)}</bpmn:documentation>' if text else ''


def node_xml(p, n, messages):
    kw = n.kw
    attrs = f'id={a(n.id)} name={a(n.name)}'
    ext = list(kw.get('ext', []))
    for e in kw.get('listeners', []):
        ext.append(listener(*e) if isinstance(e, tuple) else listener(e))
    body_ext = ext_block(ext)
    inc = ''.join(f'<bpmn:incoming>{i}</bpmn:incoming>' for i in n.incoming)
    out = ''.join(f'<bpmn:outgoing>{o}</bpmn:outgoing>' for o in n.outgoing)
    d = doc_el(kw.get('doc'))
    k = n.kind
    if k == 'businessRuleTask' and kw.get('decision'):
        # DMN direkt in der Engine (decisionRef), Ergebnis als Map in resultVariable
        attrs += (f' camunda:decisionRef={a(kw["decision"])} camunda:decisionRefBinding="latest"'
                  f' camunda:mapDecisionResult="singleResult" camunda:resultVariable={a(kw["result"])}')
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}</bpmn:{k}>'
    if k in ('serviceTask', 'sendTask', 'businessRuleTask'):
        attrs += f' camunda:type="external" camunda:topic={a(kw["topic"])}'
        loop = ''
        if kw.get('multi'):
            coll, var, seq = kw['multi']
            loop = (f'<bpmn:multiInstanceLoopCharacteristics isSequential="{str(seq).lower()}" '
                    f'camunda:collection={a(coll)} camunda:elementVariable={a(var)} />')
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}{loop}</bpmn:{k}>'
    if k == 'receiveTask':
        attrs += f' messageRef={a(kw["message"])}'
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}</bpmn:{k}>'
    if k == 'userTask':
        attrs += f' camunda:candidateGroups={a(kw["group"])}'
        if kw.get('form'):
            fields = ''
            for fdef in kw['form']:
                fid, label, typ = fdef[0], fdef[1], fdef[2]
                opts = fdef[3] if len(fdef) > 3 else {}
                inner = ''
                cons = []
                if opts.get('required'):
                    cons.append('<camunda:constraint name="required" />')
                if opts.get('readonly'):
                    cons.append('<camunda:constraint name="readonly" />')
                if cons:
                    inner += '<camunda:validation>' + ''.join(cons) + '</camunda:validation>'
                for vid, vname in opts.get('values', []):
                    inner += f'<camunda:value id={a(vid)} name={a(vname)} />'
                fields += f'<camunda:formField id={a(fid)} label={a(label)} type={a(typ)}>{inner}</camunda:formField>'
            ext.insert(0, f'<camunda:formData>{fields}</camunda:formData>')
            body_ext = ext_block(ext)
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}</bpmn:{k}>'
    if k == 'callActivity':
        attrs += f' calledElement={a(kw["called"])} camunda:calledElementBinding="latest"'
        maps = ['<camunda:in businessKey="#{execution.processBusinessKey}" />']
        maps += [f'<camunda:in source={a(v)} target={a(v)} />' for v in kw.get('ins', [])]
        maps += [f'<camunda:out source={a(v)} target={a(v)} />' for v in kw.get('outs', [])]
        body_ext = ext_block(maps + ext)
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}</bpmn:{k}>'
    if k == 'subProcess':
        kids = [nid for nid in p.order if p.nodes[nid].kw.get('parent') == n.id]
        inner = ''.join(node_xml(p, p.nodes[c], messages) for c in kids)
        inner += ''.join(flow_xml(f) for f in p.flows if p.nodes[f.src].kw.get('parent') == n.id)
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}{inner}</bpmn:{k}>'
    if k in GW_KINDS:
        dflt = [f.id for f in p.flows if f.src == n.id and f.default]
        if dflt:
            attrs += f' default={a(dflt[0])}'
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}</bpmn:{k}>'
    if k in EVENT_KINDS:
        ev = kw.get('ev')
        evdef = ''
        if ev == 'timer':
            tt, val = kw['timer']
            evdef = f'<bpmn:timerEventDefinition id={a(n.id + "_Def")}><bpmn:{tt} xsi:type="bpmn:tFormalExpression">{escape(val)}</bpmn:{tt}></bpmn:timerEventDefinition>'
        elif ev == 'message' and kw.get('topic'):
            # sendendes Nachrichten-Endereignis, ausgeführt als External Task
            evdef = (f'<bpmn:messageEventDefinition id={a(n.id + "_Def")} camunda:type="external" '
                     f'camunda:topic={a(kw["topic"])} />')
        elif ev == 'message':
            evdef = f'<bpmn:messageEventDefinition id={a(n.id + "_Def")} messageRef={a(kw["message"])} />'
        elif ev == 'conditional':
            evdef = (f'<bpmn:conditionalEventDefinition id={a(n.id + "_Def")}>'
                     f'<bpmn:condition xsi:type="bpmn:tFormalExpression">{escape(kw["condition"])}</bpmn:condition>'
                     f'</bpmn:conditionalEventDefinition>')
        if k == 'boundaryEvent':
            attrs += f' attachedToRef={a(kw["attached"])}'
            if not kw.get('interrupting', True):
                attrs += ' cancelActivity="false"'
        return f'<bpmn:{k} {attrs}>{d}{body_ext}{inc}{out}{evdef}</bpmn:{k}>'
    raise ValueError(k)


def flow_xml(f):
    attrs = f'id={a(f.id)} sourceRef={a(f.src)} targetRef={a(f.tgt)}'
    if f.name:
        attrs += f' name={a(f.name)}'
    ext = ext_block([listener(e, 'take') for e in f.listeners])
    cond = ''
    if f.cond:
        cond = f'<bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">{escape(f.cond)}</bpmn:conditionExpression>'
    return f'<bpmn:sequenceFlow {attrs}>{ext}{cond}</bpmn:sequenceFlow>'


def bounds(x, y, w, h):
    return f'<dc:Bounds x="{int(x)}" y="{int(y)}" width="{int(w)}" height="{int(h)}" />'


def wps(pts):
    return ''.join(f'<di:waypoint x="{int(x)}" y="{int(y)}" />' for x, y in pts)


def build(path, collab, processes, messages, header_comment):
    """messages: list of (id, name)."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>'] + ([f'<!-- {header_comment} -->'] if header_comment else []) + [
           '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" '
           'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
           'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" '
           'xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
           'xmlns:camunda="http://camunda.org/schema/1.0/bpmn" '
           'xmlns:bioc="http://bpmn.io/schema/bpmn/biocolor/1.0" '
           'xmlns:color="http://www.omg.org/spec/BPMN/non-normative/color/1.0" '
           'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           f'id={a("Definitions_" + processes[0].id)} targetNamespace="http://thi.de/dpe/team2" '
           'exporter="Team 2 Materialversorgung" exporterVersion="1.0">']
    # rootElements: collaboration, processes, messages
    c = [f'<bpmn:collaboration id={a(collab.id)}>']
    for pid, name, pref, *_ in collab.participants:
        c.append(f'<bpmn:participant id={a(pid)} name={a(name)}' + (f' processRef={a(pref)}' if pref else '') + ' />')
    for mid, name, src, tgt, _, _ in collab.msgflows:
        c.append(f'<bpmn:messageFlow id={a(mid)} name={a(name)} sourceRef={a(src)} targetRef={a(tgt)} />')
    c.append('</bpmn:collaboration>')
    out += c
    for p in processes:
        out.append(f'<bpmn:process id={a(p.id)} name={a(p.name)} isExecutable="{str(p.executable).lower()}" camunda:historyTimeToLive="P180D">')
        out.append(doc_el(p.doc))
        if p.lanes:
            out.append(f'<bpmn:laneSet id={a(p.id + "_LaneSet")}>')
            for lid, lname, members, *_ in p.lanes:
                out.append(f'<bpmn:lane id={a(lid)} name={a(lname)}>' + ''.join(f'<bpmn:flowNodeRef>{m}</bpmn:flowNodeRef>' for m in members) + '</bpmn:lane>')
            out.append('</bpmn:laneSet>')
        for nid in p.order:
            if not p.nodes[nid].kw.get('parent'):
                out.append(node_xml(p, p.nodes[nid], messages))
        for f in p.flows:
            if not p.nodes[f.src].kw.get('parent'):
                out.append(flow_xml(f))
        for aid, text, *_ in p.annotations:
            out.append(f'<bpmn:textAnnotation id={a(aid)}><bpmn:text>{escape(text)}</bpmn:text></bpmn:textAnnotation>')
        for sid, src, tgt, _ in p.assocs:
            out.append(f'<bpmn:association id={a(sid)} associationDirection="None" sourceRef={a(src)} targetRef={a(tgt)} />')
        out.append('</bpmn:process>')
    for mid, mname in messages:
        out.append(f'<bpmn:message id={a(mid)} name={a(mname)} />')
    # Diagram
    out.append(f'<bpmndi:BPMNDiagram id="BPMNDiagram_1"><bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement={a(collab.id)}>')
    for pid, name, pref, x, y, w, h in collab.participants:
        out.append(f'<bpmndi:BPMNShape id={a(pid + "_di")} bpmnElement={a(pid)} isHorizontal="true">{bounds(x, y, w, h)}</bpmndi:BPMNShape>')
    for p in processes:
        for lid, lname, members, x, y, w, h in p.lanes:
            out.append(f'<bpmndi:BPMNShape id={a(lid + "_di")} bpmnElement={a(lid)} isHorizontal="true">{bounds(x, y, w, h)}</bpmndi:BPMNShape>')
        for nid in p.order:
            n = p.nodes[nid]
            x, y = n.cx - n.w / 2, n.cy - n.h / 2
            extra = ' isMarkerVisible="true"' if n.kind == 'exclusiveGateway' else ''
            if n.kind == 'subProcess':
                extra = ' isExpanded="true"'
            lab = ''
            if n.kind in EVENT_KINDS or n.kind in GW_KINDS:
                if n.name:
                    lab = f'<bpmndi:BPMNLabel>{bounds(*n.label_bounds())}</bpmndi:BPMNLabel>'
            out.append(f'<bpmndi:BPMNShape id={a(nid + "_di")} bpmnElement={a(nid)}{extra}>{bounds(x, y, n.w, n.h)}{lab}</bpmndi:BPMNShape>')
        for aid, text, x, y, w, h in p.annotations:
            out.append(f'<bpmndi:BPMNShape id={a(aid + "_di")} bpmnElement={a(aid)}>{bounds(x, y, w, h)}</bpmndi:BPMNShape>')
        for sid, src, tgt, pts in p.assocs:
            out.append(f'<bpmndi:BPMNEdge id={a(sid + "_di")} bpmnElement={a(sid)}>{wps(pts)}</bpmndi:BPMNEdge>')
        for f in p.flows:
            lab = f'<bpmndi:BPMNLabel>{bounds(*flow_label_bounds(f))}</bpmndi:BPMNLabel>' if f.name else ''
            out.append(f'<bpmndi:BPMNEdge id={a(f.id + "_di")} bpmnElement={a(f.id)}>{wps(f.waypoints)}{lab}</bpmndi:BPMNEdge>')
    for mid, name, src, tgt, pts, label in collab.msgflows:
        if label:
            lx, ly, lw = label
        else:
            lx, ly, lw = pts[0][0] + 5, (pts[0][1] + pts[-1][1]) / 2 - 7, 90
        lines = max(1, (len(name) * 6 + lw - 1) // lw)
        out.append(f'<bpmndi:BPMNEdge id={a(mid + "_di")} bpmnElement={a(mid)}>{wps(pts)}'
                   f'<bpmndi:BPMNLabel>{bounds(lx, ly, lw, 14 * lines)}</bpmndi:BPMNLabel></bpmndi:BPMNEdge>')
    out.append('</bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
    out.append('</bpmn:definitions>')
    pass  # kein Abschlusskommentar
    xml = '\n'.join(s for s in out if s)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(xml + '\n')
    return xml
