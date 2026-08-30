### Trajectory — identityos_v2_semantic — req01

**03:55:07 · retrieve**
- input: Education — Bachelor's in Engineering / Technology
- action: embedding-similarity retrieval (hash): top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**03:55:07 · generate**
- input: Education — Bachelor's in Engineering / Technology
- action: call provider with cited, confidence-annotated context
- observation: Education — Bachelor's in Engineering / Technology REQUIREMENT:

**03:55:07 · verify**
- input: Education — Bachelor's in Engineering / Technology REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.00 confidence=0.00
- confidence: 0.00

**03:55:07 · bucket**
- input: Education — Bachelor's in Engineering / Technology REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: gap
- decision: gap
