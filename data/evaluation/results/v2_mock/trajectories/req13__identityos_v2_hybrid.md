### Trajectory — identityos_v2_hybrid — req13

**09:52:30 · retrieve**
- input: Languages — English, Hindi, Kannada preferred
- action: lexical retrieval, semantic fallback only if empty: 2 facts, 0 beliefs
- observation: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.
[dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.

**09:52:30 · generate**
- input: Languages — English, Hindi, Kannada preferred
- action: call provider with cited, confidence-annotated context
- observation: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.

**09:52:30 · verify**
- input: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**09:52:30 · bucket**
- input: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py)
- observation: partial
- decision: partial
