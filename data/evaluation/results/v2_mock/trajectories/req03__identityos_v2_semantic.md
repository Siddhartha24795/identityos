### Trajectory — identityos_v2_semantic — req03

**09:52:30 · retrieve**
- input: Minimum 10 years senior leadership, with a strong track record of operations leadership
- action: embedding-similarity retrieval (hash): top 1 facts, 0 beliefs
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.

**09:52:30 · generate**
- input: Minimum 10 years senior leadership, with a strong track record of operations leadership
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.

**09:52:30 · verify**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**09:52:30 · bucket**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
