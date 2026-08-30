### Trajectory — identityos_v2_semantic — req11

**09:54:24 · retrieve**
- input: Personal integrity & institutional temperament
- action: embedding-similarity retrieval (fastembed): top 3 facts, 1 beliefs
- observation: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent.
[dossier_narrative:020] (verified fact) Closing statement: describes leading the Secretariat as the most consequential work available, and explicitly invites being tested hard on the parts of the candidacy that are short rather than only the parts that are strong.
[resume:007] (verified fact) Defined evaluation frameworks pairing offline metrics with live ground-truth validation, POS-occupancy eval at approximately 87% accuracy, tracked release over release.
[belief:004] (belief, unknown, confidence=0.10) Is comfortable claiming full personal credit for joint work without qualification. — counter-evidence exists, do not state this as certain

**09:54:24 · generate**
- input: Personal integrity & institutional temperament
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent. [belief:004] (belief, unknown, confidence=0.10) Is comfortable claiming full personal credit for joint work without qualification. — counter-evidence exists, do not state this as certain

**09:54:24 · verify**
- input: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent. [belief:004] (belief, unknown, confidence=0.10) Is comfortable claiming full personal credit for joint work without qualification. — counter-evidence exists, do not state this as certain
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.80 confidence=0.42
- confidence: 0.42

**09:54:24 · bucket**
- input: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent. [belief:004] (belief, unknown, confidence=0.10) Is comfortable claiming full personal credit for joint work without qualification. — counter-evidence exists, do not state this as certain
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
