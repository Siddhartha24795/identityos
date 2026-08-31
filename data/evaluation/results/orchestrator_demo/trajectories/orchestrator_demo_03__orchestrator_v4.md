### Trajectory — orchestrator_v4 — orchestrator_demo_03

**15:07:10 · classify_intent**
- input: Please fill out the application form for this role
- action: heuristic pattern match: matched '\bfill\b'
- observation: routed to browser_fill
- confidence: 0.90
- decision: browser_fill

**15:07:10 · dispatch**
- input: Please fill out the application form for this role
- action: call services.browser_engine.agent.run_application
- observation: form_url=file:///home/siddhartha/siddhartha/features/identityos/data/applications/local_demo/application_form.html
