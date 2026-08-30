### Trajectory — identityos_v2_semantic — req11

**03:55:07 · retrieve**
- input: Personal integrity & institutional temperament
- action: embedding-similarity retrieval (hash): top 1 facts, 0 beliefs
- observation: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. States that institutional temperament means the institution outranks the incumbent, including the CEO.

**03:55:07 · generate**
- input: Personal integrity & institutional temperament
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. States that institutional temperament means the institution outranks the incumbent, including the CEO. Personal integrity & institutional temperament REQUIREMENT:

**03:55:07 · verify**
- input: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. States that institutional temperament means the institution outranks the incumbent, including the CEO. Personal integrity & institutional temperament REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.62
- confidence: 0.62

**03:55:07 · bucket**
- input: [dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. States that institutional temperament means the institution outranks the incumbent, including the CEO. Personal integrity & institutional temperament REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
