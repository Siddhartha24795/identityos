### Trajectory — baseline_rag — q17

**18:01:54 · retrieve**
- input: Do you have experience building or running a professional membership organization?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 76 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**18:01:54 · generate**
- input: Do you have experience building or running a professional membership organization?
- action: call provider with the full unstructured context dump
- observation: Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited. Siddhartha's dossier states a preference for institution-building and zero-to-one problems, describing it as "the only kind of problem I have ever been hired to solve." Siddhartha's dossier states: "I am a working generative-AI practitioner... I can tell a real deep-tech proposition from AI theatre before [an institution]'s name is on it," offered as a self-description of his professional judgment.
- decision: answered_unverified
