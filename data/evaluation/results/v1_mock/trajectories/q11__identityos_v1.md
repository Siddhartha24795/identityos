### Trajectory — identityos_v1 — q11

**18:01:54 · classify**
- input: What is your most impactful project?
- action: use declared question.type (v1 simplification, not a learned classifier)
- observation: ambiguous
- reasoning: v2 replaces this with an automatic classifier over question text alone.

**18:01:54 · retrieve**
- input: What is your most impactful project?
- action: lexical retrieval over Digital Self: top 0 facts, 0 beliefs
- observation: (no matching evidence found)

**18:01:54 · generate**
- input: What is your most impactful project?
- action: call provider with structured, citation-tagged, confidence-annotated context
- observation: What is your most impactful project?

**18:01:54 · verify**
- input: What is your most impactful project?
- action: check every sentence for an explicit citation, else a lexical grounding match
- observation: evidence_coverage=0.00 unsupported_claim_rate=1.00 overall_confidence=0.00
- confidence: 0.00

**18:01:54 · complete**
- input: q11
- action: return final answer
- observation: What is your most impactful project?
- confidence: 0.00
- decision: answered
