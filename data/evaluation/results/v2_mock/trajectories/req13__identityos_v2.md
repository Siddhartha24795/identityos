### Trajectory — identityos_v2 — req13

**03:11:45 · retrieve**
- input: Languages — English, Hindi, Kannada preferred
- action: lexical retrieval over Digital Self: top 1 facts, 0 beliefs
- observation: [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet in Kannada, and frames relocation plus Kannada learning as conditions he is committing to, not concessions being requested.

**03:11:45 · generate**
- input: Languages — English, Hindi, Kannada preferred
- action: call provider with cited, confidence-annotated context
- observation: [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet in Kannada, and frames relocation plus Kannada learning as conditions he is committing to, not concessions being requested. Languages — English, Hindi, Kannada preferred REQUIREMENT:

**03:11:45 · verify**
- input: [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet in Kannada, and frames relocation plus Kannada learning as conditions he is committing to, not concessions being requested. Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: per-sentence grounding check (same verifier as v1)
- observation: coverage=1.00 confidence=0.74
- confidence: 0.74

**03:11:45 · bucket**
- input: [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet in Kannada, and frames relocation plus Kannada learning as conditions he is committing to, not concessions being requested. Languages — English, Hindi, Kannada preferred REQUIREMENT:
- action: derive fit bucket from coverage+confidence, not a self-reported label
- observation: partial
- reasoning: A self-reported label from generation isn't independently checkable; a derived one is.
- decision: partial
