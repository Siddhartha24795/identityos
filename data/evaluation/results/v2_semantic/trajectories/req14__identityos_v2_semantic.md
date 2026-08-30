### Trajectory — identityos_v2_semantic — req14

**09:54:24 · retrieve**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
[resume:003] (verified fact) Architected a real-time CV platform processing 2000+ RTSP streams in parallel across heterogeneous cameras, codecs, and video formats.
[resume:021] (verified fact) Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.
[resume:019] (verified fact) On the AI-ML IoT Framework Team (Mar 2023 - Aug 2023), wrote plugins for object detection and tracking with different colored bounding boxes per object plus trajectory prediction, using GStreamer, TensorFlow Lite, ByteTrack, C++, and C.
[resume:005] (verified fact) Built VLM-based suspicious-event detection over live video, flagging theft, loitering, and anomalous behavior in real time with temporal context across frames.
[resume:014] (verified fact) Worked on "Generative Image Dynamics": generating a seamlessly looping video from a single image in 3 seconds, versus the best existing time of around 17 seconds, by interpreting spectral volumes as image-space modal bases that approximate object dynamics.
[resume:039] (verified fact) M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
[resume:059] (verified fact) Real-time computer-vision platform at Jinn Labs ingesting 2000+ concurrent RTSP streams with VLM-based suspicious-event detection.

**09:54:24 · generate**
- input: Desired — record of building or running a professional body (CII / NASSCOM / FICCI / AIMA)
- action: call provider with cited, confidence-annotated context
- observation: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.

**09:54:24 · verify**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**09:54:24 · bucket**
- input: [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
