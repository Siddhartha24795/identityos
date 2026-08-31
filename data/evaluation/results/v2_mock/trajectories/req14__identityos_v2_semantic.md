### Trajectory — identityos_v2_semantic — req14

**09:52:30 · retrieve**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: embedding-similarity retrieval (hash): top 3 facts, 0 beliefs
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
[dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA.
[dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.

**09:52:30 · generate**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.

**09:52:30 · verify**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**09:52:30 · bucket**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
