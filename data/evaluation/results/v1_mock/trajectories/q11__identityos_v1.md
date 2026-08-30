### Trajectory — identityos_v1 — q11

**07:00:27 · classify**
- input: What is your most impactful project?
- action: use declared question.type (v1 simplification, not a learned classifier)
- observation: ambiguous
- reasoning: v2 replaces this with an automatic classifier over question text alone.

**07:00:27 · retrieve**
- input: What is your most impactful project?
- action: lexical retrieval over Digital Self: top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**07:00:27 · generate**
- input: What is your most impactful project?
- action: call provider with structured, citation-tagged, confidence-annotated context
- observation: What is your most impactful project?

**07:00:27 · verify**
- input: What is your most impactful project?
- action: check every sentence for an explicit citation, else a lexical grounding match
- observation: evidence_coverage=0.00 unsupported_claim_rate=1.00 overall_confidence=0.00
- confidence: 0.00

**07:00:27 · complete**
- input: q11
- action: return final answer
- observation: What is your most impactful project?
- confidence: 0.00
- decision: answered
