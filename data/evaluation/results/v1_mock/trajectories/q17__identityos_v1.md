### Trajectory — identityos_v1 — q17

**09:52:29 · classify**
- input: Do you have experience building or running a professional membership organization?
- action: use declared question.type (v1 simplification, not a learned classifier)
- observation: contradictory
- reasoning: v2 replaces this with an automatic classifier over question text alone.

**09:52:29 · retrieve**
- input: Do you have experience building or running a professional membership organization?
- action: lexical retrieval over Digital Self: top 6 facts, 1 beliefs
- observation: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body.
[dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record.
[dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA.
[dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
[dossier_excerpts:012] (verified fact) Siddhartha's dossier states a preference for institution-building and zero-to-one problems, describing it as "the only kind of problem I have ever been hired to solve."
[dossier_narrative:008] (verified fact) Captain and Sports Secretary are roles given by peers and cannot be self-appointed. Professional practice of running blameless postmortems and publishing metrics that can embarrass the author. Believes institutional temperament means the institution outranks the incumbent.
[belief:003] (belief, weak inference, confidence=0.45) Considers himself an experienced builder and leader of professional/membership institutions, not just engineering teams. — counter-evidence exists, do not state this as certain

**09:52:29 · generate**
- input: Do you have experience building or running a professional membership organization?
- action: call provider with structured, citation-tagged, confidence-annotated context
- observation: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.

**09:52:29 · verify**
- input: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
- action: check every sentence for an explicit citation, else a lexical grounding match
- observation: evidence_coverage=1.00 unsupported_claim_rate=0.00 overall_confidence=0.99
- confidence: 0.99

**09:52:29 · complete**
- input: q17
- action: return final answer
- observation: [dossier_excerpts:009] (verified fact) States that the IITACB Managing Committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to a record of building or running a professional membership body. [dossier_narrative:019] (verified fact) States explicitly that the desired record of building or running a professional body (CII/NASSCOM/FICCI/AIMA) is one genuine gap, and that adjacent experience (alumni association membership, student chapter leadership) should not be treated by the committee as equivalent to that record. [dossier_excerpts:006] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA. [dossier_excerpts:008] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
- confidence: 0.99
- decision: answered
