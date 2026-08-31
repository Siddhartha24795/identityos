### Trajectory — learning_engine_v4_1 — learning_engine

**15:07:13 · experience**
- input: 14 requirements, real per-requirement results for lexical + semantic
- action: load already-committed v2_semantic run (no new LLM calls)
- observation: baseline lexical agreement=0.571, shipped hybrid agreement=0.714

**15:07:13 · hypothesis**
- input: threshold=0.0
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.571 dangerous_overclaim=0.000 n_semantic_used=0
- reasoning: rejected: agreement 0.571 does not beat the already-shipped hybrid heuristic's 0.714
- decision: reject

**15:07:13 · hypothesis**
- input: threshold=0.1
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.2
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.3
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.4
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.5
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.6
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.7
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.8
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=2
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=0.9
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=3
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · hypothesis**
- input: threshold=1.0
- action: counterfactual test: swap to semantic below this lexical-coverage threshold
- observation: agreement=0.714 dangerous_overclaim=0.000 n_semantic_used=3
- reasoning: promoted: matches/beats hybrid (0.714 >= 0.714) with zero dangerous overclaims
- decision: promote

**15:07:13 · evaluate**
- input: full 14-requirement benchmark
- action: apply promoted policy (threshold=0.1)
- observation: agreement=0.714 dangerous_overclaim=0.000
- confidence: 0.71

**15:07:13 · leave_one_out_validation**
- input: 14 folds, threshold re-selected per fold from the other 13 items
- action: apply fold-specific threshold to the held-out requirement, never trained on its own label
- observation: LOO agreement=0.714 LOO dangerous_overclaim=0.000
- reasoning: PROMPT.md: 'do not automatically trust every successful trajectory' — this is the check that the promoted rule generalizes, not just fits.
- confidence: 0.71

**15:07:13 · conclusion**
- input: 
- action: 
- observation: Promoted threshold=0.1 matches (does not exceed) the hand-designed hybrid heuristic's 0.714 agreement rate at 0.0 dangerous overclaims. This is a genuine negative-for-improvement, positive-for-validation result: an automated search over a wider hypothesis space than the hand-designed rule confirms the hand-designed rule was already at the ceiling a coverage-only signal can reach here — it does not find a better rule, it proves one wasn't being left on the table. Leave-one-out cross-validation (agreement=0.714, dangerous_overclaim=0.000) confirms this holds under held-out validation, not just a fit to all 14 items at once.
