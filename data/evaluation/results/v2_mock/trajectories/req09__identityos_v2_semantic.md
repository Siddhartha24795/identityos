### Trajectory — identityos_v2_semantic — req09

**03:55:07 · retrieve**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council)
- action: embedding-similarity retrieval (hash): top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**03:55:07 · generate**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council)
- action: call provider with cited, confidence-annotated context
- observation: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council) REQUIREMENT:

**03:55:07 · verify**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council) REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.00 confidence=0.00
- confidence: 0.00

**03:55:07 · bucket**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council) REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: gap
- decision: gap
