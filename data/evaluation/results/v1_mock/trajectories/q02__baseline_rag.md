### Trajectory — baseline_rag — q02

**17:46:25 · retrieve**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 75 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**17:46:25 · generate**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: call provider with the full unstructured context dump
- observation: M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN. Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing. Named inventor, patent Application No. 202511076834, "Generative AI based video codecs utilizing image-to-video generation", filed through Samsung Research Noida and assigned to Samsung Electronics Co., Ltd. Siddhartha's dossier states: "I am a working generative-AI practitioner... I can tell a real deep-tech proposition from AI theatre before [an institution]'s name is on it," offered as a self-description of his professional judgment.
- decision: answered_unverified
