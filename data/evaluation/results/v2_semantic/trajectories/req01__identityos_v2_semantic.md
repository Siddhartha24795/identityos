### Trajectory — identityos_v2_semantic — req01

**11:30:07 · retrieve**
- input: Education — Bachelor's in Engineering / Technology
- action: embedding-similarity retrieval (fastembed): top 6 facts, 0 beliefs
- observation: [resume:040] (verified fact) B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.
[resume:032] (verified fact) Mentored students and created content for GATE CSE.
[resume:043] (verified fact) Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing.
[resume:028] (verified fact) Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry.
[resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
[resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.

**11:30:07 · generate**
- input: Education — Bachelor's in Engineering / Technology
- action: call provider with cited, confidence-annotated context
- observation: [resume:040] (verified fact) B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.

**11:30:07 · verify**
- input: [resume:040] (verified fact) B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**11:30:07 · bucket**
- input: [resume:040] (verified fact) B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
