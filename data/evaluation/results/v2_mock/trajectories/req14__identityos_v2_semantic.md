### Trajectory — identityos_v2_semantic — req14

**03:55:07 · retrieve**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: embedding-similarity retrieval (hash): top 2 facts, 0 beliefs
- observation: [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
[dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record.

**03:55:07 · generate**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: call provider with cited, confidence-annotated context
- observation: [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA) REQUIREMENT:

**03:55:07 · verify**
- input: [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA) REQUIREMENT:
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.83
- confidence: 0.83

**03:55:07 · bucket**
- input: [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [dossier_narrative:015] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA) REQUIREMENT:
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
