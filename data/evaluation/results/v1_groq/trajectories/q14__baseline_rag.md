### Trajectory — baseline_rag — q14

**11:09:18 · retrieve**
- input: What professional body or industry association have you personally founded or run?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**11:09:44 · generate**
- input: What professional body or industry association have you personally founded or run?
- action: call provider with the full unstructured context dump
- observation: I have not founded or run a formal professional membership body such as CII, NASSCOM, FICCI or AIMA. My leadership experience to date has been in academic‑industry bridges—running unpaid guest‑lecture series, mentoring programmes, hackathon judging panels, and serving as a core member of the IIT (ISM) Dhanbad Alumni Association in Bengaluru. While I have led multiple student chapters and organized campus‑level festivals, these activities are distinct from building and managing a national‑level professional association, which I acknowledge as a genuine gap in my record.
- decision: answered_unverified
