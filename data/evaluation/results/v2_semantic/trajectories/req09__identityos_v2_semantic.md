### Trajectory — identityos_v2_semantic — req09

**03:55:28 · retrieve**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council)
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015.
[resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
[resume:031] (verified fact) Instructor, Digiimento Education Pvt. Ltd, Delhi India, Dec 2017 - June 2018.
[dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability.
[dossier_narrative:009] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job.
[resume:011] (verified fact) Staff Computer Vision Researcher, Samsung Research (AR Core Team), Noida India, Sep 2023 - Nov 2025.
[resume:061] (verified fact) Dual-processor smartwatch power management architecture at Qualcomm, increasing battery backup by about 40%.
[resume:063] (verified fact) M.Tech thesis: medical image processing using Cycle GAN at IIT (ISM) Dhanbad.

**03:55:28 · generate**
- input: Government & policy engagement (MeitY, DST, NITI Aayog, IIT Council)
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [dossier_narrative:009] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:011] (verified fact) Staff Computer Vision Researcher, Samsung Research (AR Core Team), Noida India, Sep 2023 - Nov 2025.

**03:55:28 · verify**
- input: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [dossier_narrative:009] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:011] (verified fact) Staff Computer Vision Researcher, Samsung Research (AR Core Team), Noida India, Sep 2023 - Nov 2025.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.78
- confidence: 0.78

**03:55:28 · bucket**
- input: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [dossier_narrative:009] (verified fact) Confirmed relocation to Bengaluru on appointment, accepting the role as primarily external-facing with sustained domestic travel to the 23 IIT campuses, Delhi, and industry forums nationally. States that being physically present in Bengaluru is regarded as non-negotiable for this job. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:011] (verified fact) Staff Computer Vision Researcher, Samsung Research (AR Core Team), Noida India, Sep 2023 - Nov 2025.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
