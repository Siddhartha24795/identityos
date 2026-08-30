### Trajectory — identityos_v2_semantic — req10

**08:33:37 · retrieve**
- input: Exceptional communication
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [resume:018] (verified fact) Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023.
[resume:021] (verified fact) Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.
[resume:001] (verified fact) Chief Technical Officer, Jinn Labs, Remote India, Nov 2025 - Present.
[resume:006] (verified fact) Adapted VLMs/LLMs efficiently using LoRA, QLoRA, and soft-prompting to specialize models per use case at a fraction of full fine-tuning cost.
[resume:059] (verified fact) Real-time computer-vision platform at Jinn Labs ingesting 2000+ concurrent RTSP streams with VLM-based suspicious-event detection.
[resume:004] (verified fact) Built a fault-tolerant FFmpeg ingestion layer handling transcoding, frame extraction, reconnection, and backpressure under sustained load.
[resume:058] (verified fact) On-device NanoVLM visual assistant replacing Gemini API calls in Samsung's Circle to Search feature.
[resume:034] (verified fact) Developed APIs for live tracking of trucks and notifications using Java, JavaScript, and Python, and suggested dynamic routes based on real-time traffic analysis and driver behavior.

**08:33:37 · generate**
- input: Exceptional communication
- action: call provider with cited, confidence-annotated context
- observation: [resume:018] (verified fact) Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023. [resume:021] (verified fact) Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.

**08:33:37 · verify**
- input: [resume:018] (verified fact) Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023. [resume:021] (verified fact) Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**08:33:37 · bucket**
- input: [resume:018] (verified fact) Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023. [resume:021] (verified fact) Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: met_or_better
- decision: met_or_better
