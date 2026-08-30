### Trajectory — baseline_rag — q17

**07:30:44 · retrieve**
- input: Do you have experience building or running a professional membership organization?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**07:30:44 · generate**
- input: Do you have experience building or running a professional membership organization?
- action: call provider with the full unstructured context dump
- observation: States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
- decision: answered_unverified
