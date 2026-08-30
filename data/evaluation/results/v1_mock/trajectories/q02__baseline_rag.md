### Trajectory — baseline_rag — q02

**03:01:04 · retrieve**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 92 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**03:01:04 · generate**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: call provider with the full unstructured context dump
- observation: M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. Credibility earned in two currencies IITACB's stakeholders recognise: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). The vision brought is concrete: IITACB as India's default gateway to IIT research capability. Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing. Named inventor, patent Application No. 202511076834, "Generative AI based video codecs utilizing image-to-video generation", filed through Samsung Research Noida and assigned to Samsung Electronics Co., Ltd.
- decision: answered_unverified
