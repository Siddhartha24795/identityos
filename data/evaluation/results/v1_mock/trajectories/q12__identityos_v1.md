### Trajectory — identityos_v1 — q12

**18:01:54 · classify**
- input: Describe your leadership experience.
- action: use declared question.type (v1 simplification, not a learned classifier)
- observation: ambiguous
- reasoning: v2 replaces this with an automatic classifier over question text alone.

**18:01:54 · retrieve**
- input: Describe your leadership experience.
- action: lexical retrieval over Digital Self: top 3 facts, 0 beliefs
- observation: [dossier_excerpts:009] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited.
[dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record.
[resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.

**18:01:54 · generate**
- input: Describe your leadership experience.
- action: call provider with structured, citation-tagged, confidence-annotated context
- observation: [dossier_excerpts:009] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.

**18:01:54 · verify**
- input: [dossier_excerpts:009] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.
- action: check every sentence for an explicit citation, else a lexical grounding match
- observation: evidence_coverage=1.00 unsupported_claim_rate=0.00 overall_confidence=0.99
- confidence: 0.99

**18:01:54 · complete**
- input: q12
- action: return final answer
- observation: [dossier_excerpts:009] (verified fact) Siddhartha's own dossier states his senior leadership experience has been at chief level only for the recent part of a ten-year career, in technology organizations rather than membership institutions, and that government/policy relationship-building experience at the secretariat level is being built, not inherited. [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he has no prior record of building or running a professional membership body such as CII, NASSCOM, FICCI, or AIMA, and explicitly says the committee should not be persuaded that adjacent experience (student chapters, alumni association membership) is equivalent to that record. [resume:046] (verified fact) System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.
- confidence: 0.99
- decision: answered
