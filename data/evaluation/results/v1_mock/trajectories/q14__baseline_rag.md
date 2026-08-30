### Trajectory — baseline_rag — q14

**07:00:27 · retrieve**
- input: What professional body or industry association have you personally founded or run?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**07:00:27 · generate**
- input: What professional body or industry association have you personally founded or run?
- action: call provider with the full unstructured context dump
- observation: States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. Core Member of the IIT (ISM) Dhanbad Alumni Association, active in its Bengaluru core group.
- decision: answered_unverified
