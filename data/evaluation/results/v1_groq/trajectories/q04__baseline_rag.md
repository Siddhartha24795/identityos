### Trajectory — baseline_rag — q04

**11:04:36 · retrieve**
- input: What is the application number of your filed patent on generative AI video codecs, and who is it assigned to?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**11:04:45 · generate**
- input: What is the application number of your filed patent on generative AI video codecs, and who is it assigned to?
- action: call provider with the full unstructured context dump
- observation: The patent I am listed on is **Application No. 202511076834**, titled “Generative AI based video codecs utilizing image‑to‑video generation.” It was filed through Samsung Research Noida and is **assigned to Samsung Electronics Co., Ltd.**
- decision: answered_unverified
