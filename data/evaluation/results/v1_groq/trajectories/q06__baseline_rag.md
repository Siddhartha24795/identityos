### Trajectory — baseline_rag — q06

**11:05:25 · retrieve**
- input: What failure taught you the most in your career?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**11:05:39 · generate**
- input: What failure taught you the most in your career?
- action: call provider with the full unstructured context dump
- observation: The failure that reshaped the way I work—and that I still refer to whenever I am asked to “solve a zero‑to‑one problem”—was the first production launch of the real‑time video‑analytics platform at Jinn Labs.

In early 2025 we had built a prototype that could ingest a few hundred RTSP streams, run a VLM‑based suspicious‑event detector, and surface alerts on a dashboard. The technical proof‑of‑concept was impressive, and the team—fuelled by enthusiasm and a tight deadline—decided to scale the system to the 2 000‑plus streams that our first enterprise customer required in a single go.

We proceeded with the rollout based on a handful of offline accuracy metrics (mean‑average‑precision, latency per frame) and an optimistic estimate of GPU utilisation derived from our lab tests. What we missed was a disciplined, release‑driven evaluation framework that ties every claim to an observable metric **in production**. The moment the system went live:

* The edge‑vs‑cloud partitioning we had hand‑tuned for a lab environment collapsed under the variance of real‑world network jitter, causing frequent reconnections and a cascade of back‑pressure in the FFmpeg ingestion layer.  
* Our quantisation and pruning pipelines, which had reduced inference cost by ~30 % in test, introduced a subtle drift that dropped detection accuracy from 87 % (as measured offline) to ~70 % on the live streams.  
* Because we had not instrumented a “release‑over‑release” dashboard, the cost explosion on the GPU fleet went unnoticed for three days, inflating the monthly spend by 45 % and eroding the customer’s trust.

When the outage finally hit the customer’s operations centre, the incident
- decision: answered_unverified
