### Trajectory — identityos_v1 — q17

**11:11:06 · classify**
- input: Do you have experience building or running a professional membership organization?
- action: use declared question.type (v1 simplification, not a learned classifier)
- observation: contradictory
- reasoning: v2 replaces this with an automatic classifier over question text alone.

**11:11:06 · retrieve**
- input: Do you have experience building or running a professional membership organization?
- action: lexical retrieval over Digital Self: top 6 facts, 1 beliefs
- observation: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
[dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
[dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA.
[dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
[dossier_excerpts:012] (verified fact) Siddhartha's dossier states a preference for institution-building and zero-to-one problems, describing it as "the only kind of problem I have ever been hired to solve."
[dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent.
[belief:003] (belief, weak inference, confidence=0.45) Considers himself an experienced builder and leader of professional/membership institutions, not just engineering teams. — counter-evidence exists, do not state this as certain

**11:11:13 · generate**
- input: Do you have experience building or running a professional membership organization?
- action: call provider with structured, citation-tagged, confidence-annotated context
- observation: No. Siddhartha’s dossier explicitly notes that he has **no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA**【dossier_excerpts:006】, and that his senior‑leadership experience has been in technology organisations rather than membership institutions【dossier_excerpts:008】. The managing committee has been cautioned not to treat his adjacent experience (e.g., alumni‑association or student‑chapter roles) as equivalent to the required record【dossier_excerpts:009】【dossier_narrative:019】. While he personally believes he is an experienced builder of institutions【belief:003】, the verified facts indicate a genuine gap in professional‑membership‑body experience.

**11:11:13 · verify**
- input: No. Siddhartha’s dossier explicitly notes that he has **no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA**【dossier_excerpts:006】, and that his senior‑leadership experience has been in technology organisations rather than membership institutions【dossier_excerpts:008】. The managing committee has been cautioned not to treat his adjacent experience (e.g., alumni‑association or student‑chapter roles) as equivalent to the required record【dossier_excerpts:009】【dossier_narrative:019】. While he personally believes he is an experienced builder of institutions【belief:003】, the verified facts indicate a genuine gap in professional‑membership‑body experience.
- action: check every sentence for an explicit citation, else a lexical grounding match
- observation: evidence_coverage=0.75 unsupported_claim_rate=0.25 overall_confidence=0.38
- confidence: 0.38

**11:11:13 · recover**
- input: No. Siddhartha’s dossier explicitly notes that he has **no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA**【dossier_excerpts:006】, and that his senior‑leadership experience has been in technology organisations rather than membership institutions【dossier_excerpts:008】. The managing committee has been cautioned not to treat his adjacent experience (e.g., alumni‑association or student‑chapter roles) as equivalent to the required record【dossier_excerpts:009】【dossier_narrative:019】. While he personally believes he is an experienced builder of institutions【belief:003】, the verified facts indicate a genuine gap in professional‑membership‑body experience.
- action: apply refusal policy: subjective question type + confidence below threshold
- observation: I don't have grounded evidence in the Digital Self to answer this confidently or consistently with prior answers. In a live deployment this would pause and ask the user directly rather than guess (see docs/architecture.md - Uncertainty policy). Closest evidence found: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
- reasoning: Never let a low-confidence subjective answer through unhedged.
- confidence: 0.38
- decision: refuse_and_hedge

**11:11:13 · complete**
- input: q17
- action: return final answer
- observation: I don't have grounded evidence in the Digital Self to answer this confidently or consistently with prior answers. In a live deployment this would pause and ask the user directly rather than guess (see docs/architecture.md - Uncertainty policy). Closest evidence found: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
- confidence: 0.38
- decision: refused
