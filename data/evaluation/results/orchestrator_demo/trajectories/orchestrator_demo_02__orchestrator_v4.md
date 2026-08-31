### Trajectory — orchestrator_v4 — orchestrator_demo_02

**15:07:10 · classify_intent**
- input: Does the candidate meet the requirement for deep, hands-on distributed systems experience at scale?
- action: heuristic pattern match: matched '\bdoes (the|this) candidate\b'
- observation: routed to application_fit
- confidence: 0.80
- decision: application_fit

**15:07:10 · dispatch**
- input: Does the candidate meet the requirement for deep, hands-on distributed systems experience at scale?
- action: call services.application_engine.assess.assess_identityos_hybrid
- observation: ad-hoc ApplicationRequirement built from request text; no ground truth available
