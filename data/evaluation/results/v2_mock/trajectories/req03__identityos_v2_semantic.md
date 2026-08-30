### Trajectory — identityos_v2_semantic — req03

**03:55:07 · retrieve**
- input: Minimum 10 years senior leadership, with a strong track record of operations leadership
- action: embedding-similarity retrieval (hash): top 1 facts, 0 beliefs
- observation: [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.

**03:55:07 · generate**
- input: Minimum 10 years senior leadership, with a strong track record of operations leadership
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Minimum 10 years senior leadership, with a strong track record of operations leadership REQUIREMENT:

**03:55:07 · verify**
- input: [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Minimum 10 years senior leadership, with a strong track record of operations leadership REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=0.50 confidence=0.49
- confidence: 0.49

**03:55:07 · bucket**
- input: [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Minimum 10 years senior leadership, with a strong track record of operations leadership REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
