### Trajectory — identityos_v2_semantic — req12

**09:54:08 · retrieve**
- input: Location — Bengaluru, India (domestic travel only); primarily external-facing role
- action: embedding-similarity retrieval (hash): top 1 facts, 0 beliefs
- observation: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.

**09:54:08 · generate**
- input: Location — Bengaluru, India (domestic travel only); primarily external-facing role
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.

**09:54:08 · verify**
- input: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.74
- confidence: 0.74

**09:54:08 · bucket**
- input: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
