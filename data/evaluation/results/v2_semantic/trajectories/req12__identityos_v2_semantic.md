### Trajectory — identityos_v2_semantic — req12

**08:33:37 · retrieve**
- input: Location — Bengaluru, India (domestic travel only); primarily external-facing role
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.
[dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested.
[resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015.
[resume:035] (verified fact) Full Stack Developer, Scrum Technology, Delhi India, June 2016 - Aug 2017.
[resume:033] (verified fact) Full Stack Developer, Wheelseye Technology, Gurgaon India, Sept 2017 - Dec 2017.
[dossier_excerpts:003] (verified fact) Core Member of the IIT (ISM) Dhanbad Alumni Association, active in its Bengaluru core group.
[resume:024] (verified fact) Software Engineer, Amdocs, Pune India, Aug 2020 - Feb 2021, on Billing and RTB teams.
[dossier_narrative:014] (verified fact) States a reading of the mandate: IITACB does not need a manager, it needs a founder for its second act — turning a facility and a 50,000-strong Bengaluru alumni base into an institution industry pays to join, government treats as an implementation partner, and IIT Directors route their best research through.

**08:33:37 · generate**
- input: Location — Bengaluru, India (domestic travel only); primarily external-facing role
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [resume:035] (verified fact) Full Stack Developer, Scrum Technology, Delhi India, June 2016 - Aug 2017.

**08:33:37 · verify**
- input: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [resume:035] (verified fact) Full Stack Developer, Scrum Technology, Delhi India, June 2016 - Aug 2017.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.89
- confidence: 0.89

**08:33:37 · bucket**
- input: [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [dossier_excerpts:010] (verified fact) States that relocating to Bengaluru and learning Kannada are conditions he is committing to for the IITACB CEO role specifically, not concessions being requested. [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [resume:035] (verified fact) Full Stack Developer, Scrum Technology, Delhi India, June 2016 - Aug 2017.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
