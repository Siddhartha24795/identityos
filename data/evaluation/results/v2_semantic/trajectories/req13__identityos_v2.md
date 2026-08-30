### Trajectory — identityos_v2 — req13

**07:00:43 · retrieve**
- input: Languages — English, Hindi, Kannada preferred
- action: lexical retrieval over Digital Self: top 2 facts, 0 beliefs
- observation: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.
[dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.

**07:00:43 · generate**
- input: Languages — English, Hindi, Kannada preferred
- action: call provider with cited, confidence-annotated context
- observation: [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. Languages — English, Hindi, Kannada preferred REQUIREMENT:

**07:00:43 · verify**
- input: [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: per-sentence grounding check (same verifier as v1)
- observation: coverage=1.00 confidence=0.83
- confidence: 0.83

**07:00:43 · bucket**
- input: [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: derive fit bucket from coverage+confidence, not a self-reported label
- observation: partial
- reasoning: A self-reported label from generation isn't independently checkable; a derived one is.
- decision: partial
