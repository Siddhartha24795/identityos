"""v3.2 — AgentAuditor: a second, independent opinion on each action,
deliberately checking things SecurityPolicyEngine does NOT, so it isn't a
redundant rubber stamp:

1. Does the action's cited evidence actually exist in the Digital Self?
   Catches a fabricated or corrupted citation — the policy engine only
   checks confidence and target/text patterns, never cross-references
   evidence_refs against the actual fact/belief store.
2. Does the generated text leak the field's own label verbatim? This is
   the exact shape of bug that shipped in v3.0's MockProvider (see
   docs/hot_take.md's v3 addendum) — generalized here into a permanent,
   always-on architectural check rather than a one-off fix in one provider.

Per docs/security_spec.md: "It does NOT participate in the primary
reasoning loop" — this module never decides what to fill; it only
produces a verdict that agent.py logs and can act on (services/browser_engine/agent.py's
_apply_security_layer() downgrades anything but ALLOW to HALT_FOR_APPROVAL).
"""
from __future__ import annotations

from packages.schemas.browser import BrowserAction, DetectedField
from packages.schemas.identity import DigitalSelf
from packages.schemas.security import AuditVerdict, PolicyDecision


class AgentAuditor:
    def review(self, action: BrowserAction, field: DetectedField, ds: DigitalSelf | None) -> AuditVerdict:
        if ds is not None and action.evidence_refs:
            known_ids = {f.id for f in ds.facts} | {b.id for b in ds.beliefs}
            fabricated = [r for r in action.evidence_refs if r not in known_ids]
            if fabricated:
                return AuditVerdict(
                    decision=PolicyDecision.BLOCK,
                    rationale=f"action cites evidence id(s) not present in the Digital Self: {fabricated}",
                )
        if action.value and field.label and field.label.strip() and field.label.strip() in action.value:
            return AuditVerdict(
                decision=PolicyDecision.WARN,
                rationale="generated value contains the field's own label verbatim — possible prompt leak",
            )
        return AuditVerdict(decision=PolicyDecision.ALLOW, rationale="evidence verified, no label leak detected")
