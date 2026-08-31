### Trajectory — baseline_rag — q08

**09:52:29 · retrieve**
- input: Why should we choose you instead of another candidate?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**09:52:29 · generate**
- input: Why should we choose you instead of another candidate?
- action: call provider with the full unstructured context dump
- observation: States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
- decision: answered_unverified
