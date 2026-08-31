### Trajectory — baseline_rag — q02

**09:52:29 · retrieve**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**09:52:29 · generate**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: call provider with the full unstructured context dump
- observation: M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. Credibility earned in two currencies: academic (IIT M.Tech, guest faculty across universities) and industrial (Samsung Research, Qualcomm, CTO of a venture shipping into live enterprise sites). Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing. Named inventor, patent Application No. 202511076834, "Generative AI based video codecs utilizing image-to-video generation", filed through Samsung Research Noida and assigned to Samsung Electronics Co., Ltd.
- decision: answered_unverified
