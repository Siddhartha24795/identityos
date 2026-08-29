# Research hypotheses

IdentityOS's self-improvement design (docs/roadmap.md v4) rests on four
hypotheses from the original design brief. Below: what current industry
research/practice says, plus a fifth hypothesis this v1 build surfaced
empirically — not by reading about other systems, but by running our own.

## 1. "Persistent memory does not automatically produce persistent intelligence."

**Supported.** Anthropic's May 2026 "Dreaming" feature for Claude Managed
Agents is a direct industry admission of this: raw memory accumulation is
not enough, so a separate process reviews prior sessions, merges duplicate
information, removes outdated entries, and surfaces recurring patterns
*between* sessions — memory alone doesn't do this on its own ([Anthropic
blog](https://claude.com/blog/new-in-claude-managed-agents),
[MindStudio](https://www.mindstudio.ai/blog/what-is-claude-dreaming-anthropic-agent-memory)).
Separately, "Hierarchical Memory Orchestration for Personalized Persistent
Agents" ([arXiv:2604.01670](https://arxiv.org/pdf/2604.01670)) treats raw
memory and memory *organization* as distinct engineering problems, echoing
IdentityOS's fact/belief/evidence split rather than one flat store.

## 2. "An agent should not learn from success unless it can establish why the success occurred."

**Supported, with a governance angle industry has landed on.** Anthropic's
Dreaming explicitly keeps original inputs untouched and lets teams review
changes *before* agents adopt them — success is not auto-promoted to
long-term memory without a checkable diff. "AgentLTL: A Trace-Verification
Framework..." ([arXiv:2607.02599](https://arxiv.org/pdf/2607.02599)) goes
further, formally verifying *why* a trajectory complied with a procedure
rather than just whether the outcome looked right — the same "counterfactual
before promotion" logic in docs/roadmap.md's learning engine (v4).

## 3. "The most valuable memory is not what happened, but the conditions under which a strategy is valid."

**Supported.** Dreaming's stated purpose is surfacing *conditions* —
"recurring mistakes, workflows agents converge on, preferences shared across
a team" — not raw episode logs. "Are Online Skill and Memory Modules Always
Worth Their Tokens?" ([arXiv:2606.15017](https://arxiv.org/pdf/2606.15017))
directly measures this: unconditional memory/skill modules often cost more
tokens than they save, i.e. a strategy stored without its validity
conditions is close to worthless. This is why belief:001/002 in v1's seed
set (services/identity_engine/seed_beliefs.py) carry supporting *and*
counter-evidence rather than a bare statement.

## 4. "An agent needs a model of the human it represents, not merely a collection of documents about them."

**Not directly addressed by mainstream industry research** — this is the
genuine gap. RAG-over-documents is described as "the de facto standard for
customer-facing AI agents" ([Braintrust](https://www.braintrust.dev/articles/best-hallucination-detection-tools-2026)),
but that is IdentityOS's baseline_rag, not its contribution. Personalization
research exists (recommendation systems, user-preference LLMs), but a
computational representation specifically built to *answer application
questions on a person's behalf, with provenance and refusal on
low-confidence subjective claims* does not appear to have close prior art —
this is a legitimate gap, not an oversight of the literature search.

## 5. (New, from our own v1 run) Confidence conflates source fidelity with question relevance.

Not in the original brief — discovered while scoring the v1 offline run
(docs/improvement_changelog.md, Iteration 2). A retrieved fact can be 99%
certain to be *true* and still be a poor answer to the *specific* question
asked, and v1's refusal gate only checks the former. This matches the
"defense in depth" conclusion industry has converged on — RAG grounding
reduces fabrication but doesn't by itself catch relevance mismatches
([StackAI](https://www.stackai.com/insights/prevent-ai-agent-hallucinations-in-production-environments)).
See docs/hot_take.md.

## Sources
- [New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration](https://claude.com/blog/new-in-claude-managed-agents)
- [What Is Claude Dreaming? — MindStudio](https://www.mindstudio.ai/blog/what-is-claude-dreaming-anthropic-agent-memory)
- [Hierarchical Memory Orchestration for Personalized Persistent Agents](https://arxiv.org/pdf/2604.01670)
- [Are Online Skill and Memory Modules Always Worth Their Tokens?](https://arxiv.org/pdf/2606.15017)
- [AgentLTL: A Trace-Verification Framework](https://arxiv.org/pdf/2607.02599)
- [Best hallucination detection tools for LLM applications (2026) — Braintrust](https://www.braintrust.dev/articles/best-hallucination-detection-tools-2026)
- [Prevent AI Agent Hallucinations in Production Environments — StackAI](https://www.stackai.com/insights/prevent-ai-agent-hallucinations-in-production-environments)
