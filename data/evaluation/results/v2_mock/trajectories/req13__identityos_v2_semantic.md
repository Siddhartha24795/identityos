### Trajectory — identityos_v2_semantic — req13

**03:55:07 · retrieve**
- input: Languages — English, Hindi, Kannada preferred
- action: embedding-similarity retrieval (hash): top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**03:55:07 · generate**
- input: Languages — English, Hindi, Kannada preferred
- action: call provider with cited, confidence-annotated context
- observation: Languages — English, Hindi, Kannada preferred REQUIREMENT:

**03:55:07 · verify**
- input: Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.00 confidence=0.00
- confidence: 0.00

**03:55:07 · bucket**
- input: Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: gap
- decision: gap
