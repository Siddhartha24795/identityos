### Trajectory — identityos_v2 — req10

**07:31:00 · retrieve**
- input: Exceptional communication
- action: lexical retrieval over Digital Self: top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**07:31:00 · generate**
- input: Exceptional communication
- action: call provider with cited, confidence-annotated context
- observation: Exceptional communication REQUIREMENT:

**07:31:00 · verify**
- input: Exceptional communication REQUIREMENT:
- action: per-sentence grounding check (same verifier as v1)
- observation: coverage=0.00 confidence=0.00
- confidence: 0.00

**07:31:00 · bucket**
- input: Exceptional communication REQUIREMENT:
- action: derive fit bucket from coverage+confidence, not a self-reported label
- observation: gap
- reasoning: A self-reported label from generation isn't independently checkable; a derived one is.
- decision: gap
