### Trajectory — orchestrator_v4 — orchestrator_demo_01

**15:07:10 · classify_intent**
- input: What failure taught you the most in your career?
- action: heuristic pattern match: matched '(default — no browser/fit pattern matched)'
- observation: routed to qa
- confidence: 0.50
- decision: qa

**15:07:10 · dispatch**
- input: What failure taught you the most in your career?
- action: call services.qa_engine.identityos_agent.answer_identityos
- observation: Question.type defaulted to UNSEEN_INFERENTIAL (conservative)
