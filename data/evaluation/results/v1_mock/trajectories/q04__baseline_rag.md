### Trajectory — baseline_rag — q04

**07:30:44 · retrieve**
- input: What is the application number of your filed patent on generative AI video codecs, and who is it assigned to?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**07:30:44 · generate**
- input: What is the application number of your filed patent on generative AI video codecs, and who is it assigned to?
- action: call provider with the full unstructured context dump
- observation: Named inventor, patent Application No. 202511076834, "Generative AI based video codecs utilizing image-to-video generation", filed through Samsung Research Noida and assigned to Samsung Electronics Co., Ltd. Siddhartha's stated inventorship contribution on this patent is 75%, with the remaining 25% attributed to a co-inventor who is not named in Siddhartha's own materials. Architected a real-time CV platform processing 2000+ RTSP streams in parallel across heterogeneous cameras, codecs, and video formats. Worked on "Generative Image Dynamics": generating a seamlessly looping video from a single image in 3 seconds, versus the best existing time of around 17 seconds, by interpreting spectral volumes as image-space modal bases that approximate object dynamics.
- decision: answered_unverified
