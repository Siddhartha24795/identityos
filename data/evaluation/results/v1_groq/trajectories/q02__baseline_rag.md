### Trajectory — baseline_rag — q02

**11:03:58 · retrieve**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**11:04:23 · generate**
- input: Which university awarded your M.Tech in Artificial Intelligence, and what was your research topic?
- action: call provider with the full unstructured context dump
- observation: I earned my M.Tech in Artificial Intelligence from **IIT (ISM) Dhanbad**.  My thesis focused on **medical‑image processing using Cycle‑GAN techniques**, where I explored generative adversarial networks for tasks such as image‑to‑image translation and enhancement in the medical domain.
- decision: answered_unverified
