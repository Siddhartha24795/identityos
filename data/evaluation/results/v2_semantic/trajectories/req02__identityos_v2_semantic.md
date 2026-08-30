### Trajectory — identityos_v2_semantic — req02

**09:54:23 · retrieve**
- input: Desired — IIT alumnus
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015.
[dossier_narrative:014] (verified fact) States a reading of the mandate: IITACB does not need a manager, it needs a founder for its second act — turning a facility and a 50,000-strong Bengaluru alumni base into an institution industry pays to join, government treats as an implementation partner, and IIT Directors route their best research through.
[dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.
[resume:029] (verified fact) Intern, Siemens Healthineers, Remote, July 2019 - Feb 2020.
[resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
[dossier_narrative:015] (verified fact) Proposes running IITACB as a two-sided marketplace between a curated Industry Problem Register (real, scoped, budgeted problems from member corporates) and a Faculty Capability Index across the 23 IITs, matched by someone who can assess technical viability before either side commits.
[resume:053] (verified fact) Sports Secretary 2015-2016 and Captain of the IIT Dhanbad Cricket Team; represented IIT Dhanbad at Inter-IIT in 2018 and 2019.
[dossier_narrative:009] (verified fact) States a vision specifically for the IITACB CEO role: IITACB as India's default gateway to IIT research capability, brought through the academic-and-industrial credibility described above.

**09:54:23 · generate**
- input: Desired — IIT alumnus
- action: call provider with cited, confidence-annotated context
- observation: [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [dossier_narrative:014] (verified fact) States a reading of the mandate: IITACB does not need a manager, it needs a founder for its second act — turning a facility and a 50,000-strong Bengaluru alumni base into an institution industry pays to join, government treats as an implementation partner, and IIT Directors route their best research through. [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.

**09:54:23 · verify**
- input: [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [dossier_narrative:014] (verified fact) States a reading of the mandate: IITACB does not need a manager, it needs a founder for its second act — turning a facility and a 50,000-strong Bengaluru alumni base into an institution industry pays to join, government treats as an implementation partner, and IIT Directors route their best research through. [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.83
- confidence: 0.83

**09:54:23 · bucket**
- input: [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015. [dossier_narrative:014] (verified fact) States a reading of the mandate: IITACB does not need a manager, it needs a founder for its second act — turning a facility and a 50,000-strong Bengaluru alumni base into an institution industry pays to join, government treats as an implementation partner, and IIT Directors route their best research through. [dossier_narrative:013] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the IITACB CEO role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
