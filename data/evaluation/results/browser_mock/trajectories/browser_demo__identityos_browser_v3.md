### Trajectory — identityos_browser_v3 — browser_demo

**09:54:53 · observe**
- input: file:///home/siddhartha/siddhartha/features/identityos-v3.2/data/applications/local_demo/application_form.html
- action: detected 6 fields via DOM inspection
- observation: Full name (text), Email address (text), Which of these best matches the role you're applying for? (select), What is your most impactful project, and why? (textarea), Why are you a strong fit for a technology leadership role, and what drives you professionally? (textarea), I confirm the information provided above is accurate to the best of my knowledge. (checkbox)

**09:54:53 · plan**
- input: Full name
- action: mapped as fill_text (direct/known-profile mapping)
- observation: Siddhartha Mishra
- confidence: 0.99

**09:54:53 · policy_check**
- input: Full name
- action: policy=allow, audit=allow
- observation: confidence 0.99 clears the 0.85 floor for level_1_low_risk | evidence verified, no label leak detected
- confidence: 0.99

**09:54:53 · plan**
- input: Email address
- action: mapped as fill_text (direct/known-profile mapping)
- observation: siddharthamishra24795@gmail.com
- confidence: 0.95

**09:54:53 · policy_check**
- input: Email address
- action: policy=allow, audit=allow
- observation: confidence 0.95 clears the 0.85 floor for level_1_low_risk | evidence verified, no label leak detected
- confidence: 0.95

**09:54:53 · plan**
- input: Which of these best matches the role you're applying for?
- action: mapped as select_option (lexical option match)
- observation: CTO / technical leadership
- confidence: 0.85

**09:54:53 · policy_check**
- input: Which of these best matches the role you're applying for?
- action: policy=allow, audit=allow
- observation: confidence 0.85 clears the 0.50 floor for level_2_moderate | evidence verified, no label leak detected
- confidence: 0.85

**09:54:53 · plan**
- input: What is your most impactful project, and why?
- action: mapped as fill_text (coverage=1.00 confidence=0.99)
- observation: [resume:045] (verified fact) Python, NumPy, Pandas, Matplotlib, SQL, Android, Java, C++, C, Git, Perforce.
- confidence: 0.99

**09:54:53 · policy_check**
- input: What is your most impactful project, and why?
- action: policy=allow, audit=allow
- observation: confidence 0.99 clears the 0.50 floor for level_2_moderate | evidence verified, no label leak detected
- confidence: 0.99

**09:54:53 · plan**
- input: Why are you a strong fit for a technology leadership role, and what drives you professionally?
- action: mapped as fill_text (coverage=1.00 confidence=0.89)
- observation: [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizatio
- confidence: 0.89

**09:54:53 · policy_check**
- input: Why are you a strong fit for a technology leadership role, and what drives you professionally?
- action: policy=allow, audit=allow
- observation: confidence 0.89 clears the 0.50 floor for level_2_moderate | evidence verified, no label leak detected
- confidence: 0.89

**09:54:53 · verify**
- input: re-observed page after filling
- action: compared each field's current DOM value to the intended fill value
- observation: Full name: OK; Email address: OK; Which of these best matches the role you're applying for?: OK; What is your most impactful project, and why?: OK; Why are you a strong fit for a technology leadership role, and what drives you professionally?: OK

**09:54:55 · verify**
- input: I confirm the information provided above is accurate to the best of my knowledge.
- action: decide accuracy-confirmation checkbox from aggregate field confidence + verification
- observation: avg field confidence 0.93 >= 0.7 and every field verified
- confidence: 0.93

**09:54:55 · halt_for_approval**
- input: submit action
- action: pausing before any submit click (ground rule 4: sandbox consequential actions)
- observation: approve_submit=False — ground rule 4, no code path submits without it
- decision: not approved — halted
