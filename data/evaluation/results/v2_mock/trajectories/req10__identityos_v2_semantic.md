### Trajectory — identityos_v2_semantic — req10

**03:55:07 · retrieve**
- input: Exceptional communication
- action: embedding-similarity retrieval (hash): top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**03:55:07 · generate**
- input: Exceptional communication
- action: call provider with cited, confidence-annotated context
- observation: Exceptional communication REQUIREMENT:

**03:55:07 · verify**
- input: Exceptional communication REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.00 confidence=0.00
- confidence: 0.00

**03:55:07 · bucket**
- input: Exceptional communication REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: gap
- decision: gap
