### Trajectory — baseline_rag — q14

**17:46:25 · retrieve**
- input: What professional body or industry association have you personally founded or run?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 75 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**17:46:25 · generate**
- input: What professional body or industry association have you personally founded or run?
- action: call provider with the full unstructured context dump
- observation: Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. Core Member of the IIT (ISM) Dhanbad Alumni Association, active in its Bengaluru core group. Siddhartha's dossier states: "I am a working generative-AI practitioner... I can tell a real deep-tech proposition from AI theatre before [an institution]'s name is on it," offered as a self-description of his professional judgment. Siddhartha's dossier states a preference for institution-building and zero-to-one problems, describing it as "the only kind of problem I have ever been hired to solve."
- decision: answered_unverified
