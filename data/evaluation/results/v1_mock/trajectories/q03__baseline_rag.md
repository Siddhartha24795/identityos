### Trajectory — baseline_rag — q03

**17:46:25 · retrieve**
- input: What battery-life improvement did your dual-processor architecture achieve on Qualcomm smartwatches?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 75 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**17:46:25 · generate**
- input: What battery-life improvement did your dual-processor architecture achieve on Qualcomm smartwatches?
- action: call provider with the full unstructured context dump
- observation: Dual-processor smartwatch power management architecture at Qualcomm, increasing battery backup by about 40%. Increased smartwatch battery backup by around 40% using a dual-processor concept that offloaded display and controls to a secondary processor. Leads a 35+ member cross-functional team (CV/ML research, edge and cloud infra, backend, frontend) as Head of Engineering and Innovation, owning hiring, roadmap, architecture review, and delivery. Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023.
- decision: answered_unverified
