### Trajectory — baseline_rag — q12

**04:41:12 · retrieve**
- input: Describe your leadership experience.
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**04:41:12 · generate**
- input: Describe your leadership experience.
- action: call provider with the full unstructured context dump
- observation: Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited. States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. Ten years in the profession (2016-2026) across Scrum Technology, Wheelseye, Amdocs, Qualcomm, Samsung Research and Jinn Labs, the last five in lead, staff and chief roles. Operations leadership here is not theoretical — it is 24x7 production accountability across live customer sites.
- decision: answered_unverified
