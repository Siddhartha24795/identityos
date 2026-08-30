### Trajectory — identityos_v2_semantic — req01

**03:55:27 · retrieve**
- input: Education — Bachelor's in Engineering / Technology
- action: embedding-similarity retrieval (fastembed): top 7 facts, 0 beliefs
- observation: [resume:040] (verified fact) B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.
[resume:032] (verified fact) Mentored students and created content for GATE CSE.
[resume:043] (verified fact) Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing.
[resume:028] (verified fact) Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry.
[dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability.
[resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
[resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.

**03:55:27 · generate**
- input: Education — Bachelor's in Engineering / Technology
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [resume:028] (verified fact) Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.

**03:55:27 · verify**
- input: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [resume:028] (verified fact) Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.83
- confidence: 0.83

**03:55:27 · bucket**
- input: [dossier_narrative:002] (verified fact) Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. [resume:028] (verified fact) Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry. [resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
