# Original design brief

This is the full, unedited brief IdentityOS was designed against. It
describes a system considerably larger than any single version in
docs/roadmap.md — see docs/architecture.md for what v1 actually builds and
why, and docs/roadmap.md for what's deferred to which later version.

---

You are the lead architect and implementation engineer for a research-grade autonomous agent system.

Your task is to BUILD the complete system described below, not just propose an architecture.

Do not give me a superficial demo, toy workflow, static mockup, or chatbot wrapper.

The goal is to build a genuinely ambitious agentic system that could be presented as a serious agentic-AI research prototype while still being runnable as a hackathon project.

============================================================
PROJECT THEME
============================================================

PROJECT NAME:

IDENTITYOS
"An Autonomous Personal Representation Engine"

Core thesis:

Today's agents can browse websites, reason, call tools, fill forms, search documents, write applications, and orchestrate other agents.

But they do not truly understand the PERSON they are representing.

A human applying for a job, internship, PhD, fellowship, research program, grant, accelerator, scholarship, visa, conference, or similar opportunity is repeatedly forced to reconstruct themselves from scattered information:

- CV
- LinkedIn
- GitHub
- publications
- research projects
- portfolios
- previous applications
- SOPs
- cover letters
- emails
- presentations
- documents
- achievements
- preferences
- goals
- previous decisions
- writing style
- implicit motivations
- personal stories
- career trajectory

The real problem is not:

"How do we fill a form?"

The real problem is:

"How would this particular human answer a question that they have never explicitly answered before?"

IDENTITYOS should solve this.

The system should construct a continuously evolving computational representation of a human and then use that representation to autonomously understand and execute unfamiliar applications.

The system should behave as an autonomous representative of the user.

============================================================
PRIMARY PROBLEM STATEMENT
============================================================

Build an agent capable of transforming scattered information about a person into a verified, continuously improving "Digital Self" capable of:

1. understanding who the person is,
2. understanding what they have done,
3. understanding what they believe,
4. understanding their preferences,
5. understanding their goals,
6. understanding how they communicate,
7. understanding recurring themes in their decisions,
8. answering previously unseen questions in a way consistent with the person,
9. generating application-specific content,
10. navigating arbitrary websites,
11. discovering application requirements,
12. filling forms,
13. uploading documents,
14. adapting to changing form layouts,
15. handling browser workflows,
16. preserving consistency across applications,
17. learning from outcomes,
18. detecting uncertainty and unsupported assumptions,
19. preventing hallucinated personal information,
20. continuously improving its representation of the user.

The central research question:

"Can an AI become a faithful computational extension of a human's professional identity and decision-making process without turning into a hallucinated version of that human?"

============================================================
IMPORTANT DESIGN PRINCIPLE
============================================================

Do NOT build:

CV parser + chatbot + browser automation.

That is too simple.

Build:

HUMAN
  |
IDENTITY INGESTION
  |
PERSONAL WORLD MODEL
  |
MEMORY + EXPERIENCE GRAPH
  |
BELIEF / PREFERENCE MODEL
  |
REASONING ABOUT THE PERSON
  |
APPLICATION UNDERSTANDING
  |
APPLICATION STRATEGY
  |
CONTENT GENERATION
  |
VERIFICATION
  |
BROWSER EXECUTION
  |
OUTCOME
  |
LEARNING
  |
UPDATED DIGITAL SELF

The architecture must explicitly separate:

A. facts
B. memories
C. beliefs
D. inferred preferences
E. goals
F. historical states
G. uncertain assumptions
H. evidence
I. writing style
J. application-specific strategy

============================================================
SYSTEM VISION
============================================================

The user should initially provide some combination of:

- LinkedIn URL
- GitHub URL
- personal website
- CV / resume
- academic transcripts if desired
- publications
- Google Drive folder
- portfolio
- existing SOPs
- previous job applications
- cover letters
- project documents
- research notes
- other user-approved sources

The system ingests these sources.

It creates a "Digital Self".

The Digital Self should contain:

------------------------------------------------------------
1. FACT MEMORY
------------------------------------------------------------

Examples:

Education
Employment
Projects
Publications
Awards
Skills
Locations
Dates
Organizations
Technologies
Achievements

Every important fact must have provenance.

Example:

FACT:
"Built on-device diffusion model optimization pipeline."

SOURCE:
resume.pdf page 3

CONFIDENCE:
0.99

------------------------------------------------------------
2. EPISODIC MEMORY
------------------------------------------------------------

Store important experiences.

Example:

EVENT:
"Presented a computer-vision project to senior leadership."

Store:

- date
- context
- actors
- action
- result
- evidence
- importance

------------------------------------------------------------
3. SEMANTIC MEMORY
------------------------------------------------------------

Knowledge about the person that emerges across many documents.

Example:

"Frequently works on difficult ML systems problems."

------------------------------------------------------------
4. BELIEF MODEL
------------------------------------------------------------

Infer statements such as:

"Prefers technically challenging problems."

"Values ownership."

"Interested in research + production."

Each belief must store:

- supporting evidence
- counter-evidence
- confidence
- timestamp
- last validation
- source references

Never treat inferred beliefs as facts.

------------------------------------------------------------
5. GOAL MODEL
------------------------------------------------------------

Store:

Current goals
Long-term goals
Past goals
Abandoned goals
Potential goals
Conflicting goals

Goals must have temporal validity.

A goal from 2022 must not blindly override a goal inferred in 2026.

------------------------------------------------------------
6. COMMUNICATION MODEL
------------------------------------------------------------

Learn:

- vocabulary
- sentence structure
- preferred level of technicality
- writing density
- formality
- recurring phrases
- storytelling style
- degree of directness
- preferred narrative structure

Do not imitate superficial stylistic quirks only.

The goal is semantic/personality consistency.

------------------------------------------------------------
7. DECISION MODEL
------------------------------------------------------------

Store historical decisions.

Examples:

Why did the user leave a role?

Why did they select a project?

Why did they reject an opportunity?

Why did they pursue a particular research area?

This is critical for answering future questions about motivation.

------------------------------------------------------------
8. CONTRADICTION GRAPH
------------------------------------------------------------

The system must detect contradictions.

Example:

2024:
"I want to focus entirely on research."

2026:
"I want to build production systems."

Do not silently merge these.

Represent:

BELIEF A
BELIEF B
TIME
CONTEXT
POSSIBLE EVOLUTION

The system should determine whether this represents:

- actual contradiction,
- changing preference,
- contextual difference,
- ambiguity.

============================================================
THE IDENTITY GRAPH
============================================================

Implement an explicit graph structure.

Nodes:

Person
Fact
Experience
Project
Skill
Organization
Publication
Goal
Belief
Preference
Decision
Story
Document
Question
Application
Outcome

Edges:

SUPPORTED_BY
CONTRADICTS
DERIVED_FROM
RELATED_TO
PRECEDES
CAUSED
DEMONSTRATES
REINFORCES
WEAKENS
EXPIRES
SUPERSEDES

This should NOT be simply a vector database.

Use hybrid memory:

- relational store / graph
- vector store
- document store
- structured JSON representations
- temporal metadata

Use embeddings for semantic retrieval, but do not use embeddings as the sole memory mechanism.

============================================================
THE CORE INNOVATION
============================================================

Implement:

"Identity Compilation"

Input:

Human Identity Model

Output:

Application-Specific Identity Representation

For every application, create:

APPLICATION_INTENT_MODEL

containing:

- what the organization wants
- what they value
- required qualifications
- hidden signals
- questions
- narrative opportunities
- evidence required
- likely evaluation criteria
- user-fit dimensions

Then compile the Digital Self into an application-specific strategy.

For example:

Human identity:
"Research-oriented ML engineer"

Application:
"Computer Vision Research Internship"

The agent should automatically identify:

Relevant projects
Relevant publications
Relevant achievements
Relevant narrative
Relevant motivation
Relevant technical depth

Then generate:

SOP
cover letter
short answers
research statement
project descriptions
answers to behavioral questions
application metadata

without requiring the user to manually reconstruct their history every time.

============================================================
UNSEEN QUESTION REASONING
============================================================

This is one of the most important components.

Suppose the person has never answered:

"What research problem would you spend the next five years solving?"

There may be no exact answer in memory.

The system must perform:

QUESTION
-> QUESTION TYPE CLASSIFICATION
-> LATENT PERSONAL DIMENSIONS REQUIRED
-> EVIDENCE RETRIEVAL
-> CANDIDATE INTERPRETATIONS
-> BELIEF / GOAL REASONING
-> COUNTER-EVIDENCE CHECK
-> ANSWER GENERATION
-> FACT CHECK
-> IDENTITY CONSISTENCY CHECK
-> STYLE CHECK
-> FINAL ANSWER

The system must distinguish:

KNOWN FACT
STRONG INFERENCE
WEAK INFERENCE
UNKNOWN

If confidence is low, the system may ask the user.

Otherwise, it should autonomously reason from evidence.

============================================================
AGENT ORGANIZATION
============================================================

Do NOT create 20 agents just for the sake of saying "multi-agent".

Use specialized agents only where they provide measurable value.

Recommended architecture:

                    ORCHESTRATOR
                         |
        +----------------+----------------+
        |                |                |
   Identity Agent   Opportunity Agent  Browser Agent
        |                |                |
        +----------------+----------------+
                         |
                  Application Planner
                         |
        +----------------+----------------+
        |                |                |
   Evidence Agent   Writing Agent    Strategy Agent
        |                |                |
        +----------------+----------------+
                         |
                    Verification
                         |
        +----------------+----------------+
        |                |                |
 Identity Judge   Evidence Judge    Contradiction Judge
        |                |                |
        +----------------+----------------+
                         |
                  Browser Execution
                         |
                      Outcome
                         |
                  Learning Engine

Potential specialized agents:

1. Identity Analyst
2. Evidence Retriever
3. Opportunity Analyst
4. Application Planner
5. Personal Narrative Generator
6. Browser Agent
7. Visual Form Understanding Agent
8. Verification Agent
9. Contradiction Agent
10. Outcome Learning Agent

The orchestrator must dynamically decide which agents are actually necessary.

============================================================
BROWSER AUTOMATION
============================================================

Build a real browser agent.

Preferred stack:

- Playwright
- browser-use where useful
- computer-use/VLM capability
- DOM inspection
- screenshots
- OCR only when necessary
- accessibility tree
- network/event observation when appropriate

The system must be able to:

1. open a website,
2. understand page structure,
3. identify application links,
4. navigate multi-step workflows,
5. detect forms,
6. infer field semantics,
7. map fields to IdentityOS data,
8. generate answers,
9. fill text fields,
10. select options,
11. upload documents,
12. handle dynamic forms,
13. recover from unexpected layout changes,
14. verify entered values,
15. detect missing fields,
16. detect validation errors,
17. retry with a different strategy,
18. maintain state across pages.

Do not hard-code one company's website.

Build a generalized browser execution abstraction.

Example:

BrowserObservation

{
  url,
  title,
  screenshot,
  DOM,
  accessibility_tree,
  visible_text,
  forms,
  buttons,
  inputs,
  errors
}

Then:

BrowserAction

{
  action_type,
  target,
  value,
  rationale,
  confidence
}

============================================================
OTP / LOGIN / AUTHENTICATION
============================================================

Authentication must be handled through legitimate user-authorized mechanisms.

Support:

- user login
- password manager integration where explicitly authorized
- OAuth
- API-based authentication when legitimately available
- email access through authorized connectors
- OTP retrieval from an authorized mailbox if explicitly configured

Do NOT bypass MFA, CAPTCHA, anti-bot protections, access controls, identity verification, or security mechanisms.

If an OTP requires direct user confirmation, pause and request it.

The architecture should make this a human-in-the-loop checkpoint rather than attempting to defeat security.

For the hackathon, keep consequential final submission actions sandboxed or explicitly approval-gated in accordance with the challenge rules.

============================================================
APPLICATION TYPES
============================================================

Support a broad abstraction capable of handling:

JOB APPLICATION

INTERNSHIP APPLICATION

PHD APPLICATION

RESEARCH INTERNSHIP

FELLOWSHIP

SCHOLARSHIP

GRANT

ACCELERATOR

STARTUP APPLICATION

CONFERENCE SUBMISSION

RESEARCH PROGRAM

VISA / ADMINISTRATIVE FORM where appropriate

The architecture should be extensible.

============================================================
DOCUMENT GENERATION
============================================================

Implement generators for:

- CV customization
- cover letter
- SOP
- personal statement
- research statement
- research proposal
- motivation letter
- behavioral answers
- technical answers
- short-form answers
- long-form essays
- project descriptions
- publication summaries
- portfolio descriptions

Every generated claim should be traceable.

Example internal representation:

{
  "claim": "...",
  "evidence": [
      "resume.pdf:p3",
      "github:repo-x"
  ],
  "confidence": 0.94,
  "type": "verified_fact"
}

============================================================
APPLICATION STRATEGY
============================================================

The agent should NOT simply answer all questions independently.

First understand the entire application.

Example:

Question 1:
Why this company?

Question 2:
Most impactful project?

Question 3:
Biggest challenge?

Question 4:
Future goals?

The agent should build a global narrative plan.

Then answer the questions as a coherent set.

Avoid:

Q1 talking about research
Q2 talking about management
Q3 talking about entrepreneurship
Q4 talking about completely unrelated goals

unless this is actually representative of the person.

Implement:

APPLICATION_NARRATIVE_STATE

containing:

Core narrative
Supporting stories
Repeated themes
Evidence allocation
Questions already answered
Claims already used
Potential contradictions
Unused strong evidence

============================================================
SELF-IMPROVEMENT ENGINE
============================================================

This is the main research component.

Do NOT simply save chat history.

After each application workflow:

1. collect trajectory,
2. collect failures,
3. collect successful actions,
4. compare expected vs observed,
5. identify root causes,
6. determine whether a learning event exists,
7. generate candidate improvement,
8. test it offline,
9. verify it,
10. decide whether to add it to long-term memory.

Use:

EXPERIENCE
-> FAILURE ANALYSIS
-> HYPOTHESIS
-> CANDIDATE IMPROVEMENT
-> COUNTERFACTUAL TEST
-> EVALUATION
-> PROMOTION / REJECTION

The agent should NOT automatically trust every successful trajectory.

This is critical.

A successful outcome may be:

- genuine learning,
- lucky execution,
- benchmark exploitation,
- environment-specific behavior,
- irrelevant coincidence.

The system must distinguish these.

============================================================
META-LEARNING
============================================================

Build a mechanism capable of learning:

"When should I use a particular strategy?"

Instead of only storing:

"Strategy X works."

Store:

"Strategy X tends to work under conditions A/B/C."

For example:

Strategy:
"Use detailed project narrative."

Valid when:
Research application
Long answer field
Technical reviewer

Invalid when:
100-character application field

The learned knowledge therefore becomes conditional.

============================================================
COUNTERFACTUAL EVALUATION
============================================================

When possible, test:

Would the learned rule still work if:

- the question wording changed?
- another organization asked it?
- the evidence order changed?
- the website layout changed?
- the application type changed?

This should prevent overfitting.

============================================================
DIGITAL SELF VERSIONING
============================================================

Treat the Digital Self as versioned state.

Example:

Digital Self v1
Digital Self v2
Digital Self v3

Each update must contain:

- what changed
- why
- evidence
- confidence
- source
- timestamp
- old state
- new state

The system should support rollback.

============================================================
UNCERTAINTY
============================================================

Every nontrivial inference must carry confidence.

Example:

0.99 verified fact
0.90 strong inference
0.70 moderate inference
0.40 weak inference

Do NOT hallucinate certainty.

Introduce a policy:

IF confidence < threshold
AND question requires subjective personal information

THEN ask the user.

Otherwise continue autonomously.

The user should NOT be asked trivial questions repeatedly.

============================================================
USER INVOLVEMENT
============================================================

The user's involvement should approach zero for routine tasks.

The ideal workflow is:

USER:

"Apply me to this research internship."

or:

"Find suitable opportunities this week."

Then:

Agent discovers opportunity
-> reads requirements
-> checks eligibility
-> builds strategy
-> generates documents
-> opens application
-> fills fields
-> uploads documents
-> handles workflow
-> verifies consistency
-> records trajectory
-> updates Digital Self

Only request user intervention for:

- genuinely unknown personal information
- low-confidence identity inference
- authentication that requires direct user action
- security challenges
- legally consequential confirmation
- final consequential submission where required

Do not interrupt the user merely because the agent is uncertain about something that can be resolved from evidence.

============================================================
OPPORTUNITY DISCOVERY
============================================================

Also build an opportunity discovery agent.

Inputs:

- LinkedIn
- company career pages
- university pages
- research lab pages
- fellowship sites
- startup programs
- job boards
- user-provided URLs

The agent should evaluate:

FIT =

skills
+ research alignment
+ experience
+ goals
+ location
+ seniority
+ requirements
+ probability of success

Then rank opportunities.

Do not optimize solely for probability of acceptance.

The best opportunity should maximize:

USER_VALUE

which may incorporate:

career trajectory
research alignment
learning value
compensation
location
prestige
technical depth
growth potential

Make the scoring configurable.

============================================================
APPLICATION MEMORY
============================================================

Store every application as an object:

Application {
    organization
    role
    source_url
    date
    requirements
    generated_documents
    answers
    evidence
    narrative_strategy
    browser_trajectory
    failures
    retries
    outcome
}

This creates longitudinal learning.

============================================================
TRAJECTORY LOGGING
============================================================

Every agent action must be observable.

Log:

timestamp
agent
input
observation
reason
tool
action
result
error
retry
confidence
decision

The UI should allow viewing a trajectory.

Example:

09:41
Opportunity Agent
Detected application.

09:42
Identity Agent
Matched "on-device diffusion optimization"
with requirement #4.

09:43
Writing Agent
Generated project narrative.

09:44
Verifier
Rejected narrative because claim lacked sufficient evidence.

09:45
Evidence Agent
Retrieved project report.

09:46
Writing Agent
Regenerated answer.

This is essential for judging and research analysis.

============================================================
VERIFICATION
============================================================

Implement multiple verification dimensions.

1. FACTUAL VERIFICATION
Does the claim exist in source data?

2. IDENTITY VERIFICATION
Does this actually represent the person?

3. CONTRADICTION VERIFICATION
Does it conflict with previous answers?

4. STYLE VERIFICATION
Does the text match the user's communication profile?

5. APPLICATION VERIFICATION
Does the answer actually address what the organization asked?

6. COMPLETENESS VERIFICATION
Did we miss any required field?

7. BROWSER VERIFICATION
Was the entered value actually saved?

============================================================
VLM COMPONENT
============================================================

Use a VLM where visual reasoning provides genuine value.

The VLM should interpret:

- screenshots
- visual form layouts
- unusual UI components
- graphical buttons
- dynamically rendered forms
- multi-column forms
- canvas-like controls
- visual validation states

The browser system should combine:

DOM reasoning
+
accessibility tree
+
text
+
screenshot/VLM reasoning

Do not use the VLM everywhere.

Use it when visual understanding is actually needed.

============================================================
SELF-EVALUATION
============================================================

Create a benchmark.

At least 20-50 application questions.

Include:

normal questions
unseen questions
ambiguous questions
contradictory questions
adversarial questions
questions requiring personal inference
questions requiring long-term history

Compare:

BASELINE 1:
Plain LLM prompt

BASELINE 2:
LLM + resume RAG

BASELINE 3:
LLM + resume + profile

SYSTEM:
IdentityOS

Measure:

1. factual accuracy
2. hallucination rate
3. unsupported claim rate
4. contradiction rate
5. identity fidelity
6. evidence coverage
7. application quality
8. completion success
9. human intervention count
10. task completion time
11. cost
12. browser recovery rate

Most important metric:

IDENTITY FIDELITY SCORE

Define a reproducible scoring system.

============================================================
IDENTITY FIDELITY BENCHMARK
============================================================

Create a dataset of questions answered independently by the actual user.

Important:

The evaluation set must include questions that the agent has NEVER seen.

Compare:

REAL HUMAN ANSWER
vs
IDENTITYOS ANSWER
vs
GENERIC LLM ANSWER
vs
RAG-ONLY ANSWER

Evaluate:

semantic consistency
factual consistency
preference consistency
narrative consistency
style similarity

Also evaluate whether a qualified reviewer can identify unsupported claims.

============================================================
HARD CASES
============================================================

The demo MUST include difficult cases.

Example:

The application asks:

"What failure taught you the most?"

But the user never answered this exact question.

Another:

"What motivates your research?"

Another:

"Why should we choose you instead of another candidate?"

Another:

"Where do you see yourself in five years?"

Another:

"Tell us about a decision that changed your career."

These are not retrieval problems.

They require reasoning about the human.

============================================================
USER INTERFACE
============================================================

Build a polished web interface.

Recommended:

Frontend:
Next.js / React

Backend:
Python + FastAPI

Agent framework:
Use a modular approach; do not tightly couple business logic to one framework.

Storage:

PostgreSQL
+ pgvector

Optionally:

Neo4j for identity graph

Redis for task state

Object storage for documents

The UI should have:

------------------------------------------------------------
Dashboard
------------------------------------------------------------

Digital Self health

Applications
Opportunities
Recent learning
Confidence
Contradictions
Pending user input
Agent activity

------------------------------------------------------------
Digital Self Explorer
------------------------------------------------------------

Show:

facts
beliefs
goals
experiences
skills
projects
stories
decisions
contradictions
evidence

Allow drilling into provenance.

------------------------------------------------------------
Opportunity Feed
------------------------------------------------------------

Show discovered opportunities with fit scores.

------------------------------------------------------------
Application Workspace
------------------------------------------------------------

Show:

application
questions
answers
evidence
confidence
browser execution
trajectory
status

------------------------------------------------------------
Agent Trajectory View
------------------------------------------------------------

Timeline of agent decisions.

------------------------------------------------------------
Identity Diff
------------------------------------------------------------

Show:

Before Digital Self
After Digital Self

This is very important for demonstrating learning.

============================================================
ARCHITECTURE REQUIREMENTS
============================================================

Create a clean monorepo.

Suggested:

/apps
  /web

/services
  /api
  /agent_orchestrator
  /browser_agent
  /identity_engine
  /memory_engine
  /evaluation_engine
  /learning_engine

/packages
  /schemas
  /prompts
  /tools
  /observability

/data
  /examples
  /evaluation

/docs

The exact structure can change if you have a better engineering reason.

Use:

- typed schemas
- Pydantic models
- structured tool calls
- event-driven agent state
- persistent task state
- retries
- timeouts
- tracing
- structured logs

============================================================
MODEL ABSTRACTION
============================================================

Do not hardcode the system to one model.

Create an LLM provider abstraction.

Support configuration for:

OpenAI
Anthropic
Google
local models

Potential VLM providers:

GPT-class multimodal model
Claude vision
Gemini
local VLM

The application should work using environment configuration.

============================================================
AGENT STATE MACHINE
============================================================

Implement explicit states:

DISCOVER
UNDERSTAND
PLAN
RETRIEVE
GENERATE
VERIFY
EXECUTE
OBSERVE
RECOVER
LEARN
COMPLETE

Every state should be resumable.

Failures must not corrupt the application state.

============================================================
RECOVERY
============================================================

Browser failures should not simply terminate.

Examples:

Element not found
-> inspect DOM

Still not found
-> screenshot/VLM

Still ambiguous
-> alternate locator

Still failing
-> rethink action

Validation failure
-> inspect error

Persistent failure
-> application-specific recovery strategy

Record what worked.

============================================================
SECURITY
============================================================

Treat all external content as untrusted.

Protect against:

prompt injection
malicious webpage instructions
tool poisoning
indirect prompt injection
malicious uploaded files
credential leakage
cross-application data leakage

NEVER allow a webpage to redefine the agent's system instructions.

Use strict tool permission boundaries.

Credentials must never appear in logs.

============================================================
PRIVACY
============================================================

The system is handling extremely sensitive personal information.

Implement:

encrypted secrets
access controls
isolated application sessions
audit logs
credential redaction
data deletion
source-level permissions

Only use user-authorized data.

============================================================
ETHICAL CONSTRAINT
============================================================

The system represents the user truthfully.

It must never invent:

employment
degrees
publications
skills
awards
projects
personal experiences
research
achievements
motivations

The objective is faithful representation, not maximizing acceptance through deception.

============================================================
SELF-IMPROVEMENT RESEARCH LOOP
============================================================

Implement this explicitly:

                         EXPERIENCE
                              |
                              v
                       TRAJECTORY ANALYSIS
                              |
                              v
                         FAILURE MODEL
                              |
                              v
                     IMPROVEMENT HYPOTHESIS
                              |
                              v
                      COUNTERFACTUAL TEST
                              |
                              v
                         EVALUATION
                         /          \
                    FAIL            PASS
                     |                |
                  REJECT            PROMOTE
                                      |
                                      v
                           UPDATE DIGITAL SELF
                                      |
                                      v
                            FUTURE APPLICATIONS

Do NOT let an agent modify itself arbitrarily.

All persistent learning should be validated.

============================================================
THE "SECOND BRAIN" CONCEPT
============================================================

The system should eventually become a computational second brain for the user's professional life.

It should know:

"What has this person actually done?"

"What does this person care about?"

"What does this person repeatedly choose?"

"What changed over time?"

"What evidence supports this?"

"What is uncertain?"

"What would this person probably say?"

"What should NOT be claimed?"

This is the central product identity.

============================================================
DEMO SCENARIO
============================================================

Build a complete end-to-end demo.

Input:

User provides:

CV
LinkedIn
GitHub
previous SOP
portfolio

Then user provides one job/research application URL.

The system:

1. ingests user data
2. builds Digital Self
3. opens application
4. understands company/university
5. analyzes role
6. determines fit
7. builds application strategy
8. generates required documents
9. answers unseen questions
10. verifies evidence
11. opens browser
12. fills application
13. uploads files
14. handles multi-page navigation
15. detects errors
16. recovers
17. verifies final state
18. records trajectory
19. stores application memory
20. identifies what it learned
21. updates Digital Self
22. produces final report

The entire flow should be demonstrable.

============================================================
HACKATHON ALIGNMENT
============================================================

The uploaded hackathon brief emphasizes:

- meaningful user problem
- purposeful agent capabilities
- baseline comparison
- improvement changelog
- measurable evaluation
- reproducibility
- agent trajectories
- feedback
- retries
- human checkpoints

Design the repository so that these are first-class artifacts.

Create:

/docs/problem_statement.md
/docs/architecture.md
/docs/evaluation.md
/docs/improvement_changelog.md
/docs/research_hypothesis.md
/docs/demo_script.md
/docs/hot_take.md

Also generate representative trajectory files.

============================================================
IMPROVEMENT CHANGELOG
============================================================

Structure experiments as:

Baseline
Iteration 1
Iteration 2
Iteration 3
...
Final

For every experiment record:

Problem observed
Hypothesis
Change made
Evaluation
Result
Decision
Learning

Include failed experiments.

Do not hide failures.

============================================================
HOT TAKE / RESEARCH INSIGHT
============================================================

The system should investigate this hypothesis:

"Persistent memory does not automatically produce persistent intelligence."

A second hypothesis:

"An agent should not learn from success unless it can establish why the success occurred."

A third:

"The most valuable memory is not what happened, but the conditions under which a strategy is valid."

A fourth:

"An agent needs a model of the human it represents, not merely a collection of documents about them."

Test these hypotheses experimentally.

============================================================
DELIVERABLES
============================================================

Build the entire repository.

Deliver:

1. working backend
2. working frontend
3. agent orchestration
4. identity engine
5. memory engine
6. browser agent
7. VLM integration
8. application analyzer
9. document generator
10. verification system
11. learning engine
12. evaluation suite
13. trajectory viewer
14. Docker setup
15. README
16. environment template
17. seed demo data
18. sample applications
19. reproducible benchmark
20. improvement changelog

============================================================
IMPLEMENTATION BEHAVIOR
============================================================

Do not spend the entire response explaining what you are going to build.

Start by inspecting the environment.

Then:

1. create repository structure,
2. define schemas,
3. implement core backend,
4. implement identity engine,
5. implement memory,
6. implement agent orchestration,
7. implement browser agent,
8. implement application understanding,
9. implement generation,
10. implement verification,
11. implement self-improvement,
12. implement evaluation,
13. implement UI,
14. integrate everything,
15. run tests,
16. fix failures,
17. run an end-to-end demo,
18. document the results.

When an architectural decision is required, choose a technically defensible option and continue implementation instead of repeatedly asking for confirmation.

Use production-quality code where practical.

Do not create fake integrations that are presented as working integrations.

When an external credential or API is unavailable, provide a clean adapter and a working local/mock implementation so the complete architecture can still be demonstrated.

============================================================
FINAL STANDARD
============================================================

The finished system must feel like:

"An autonomous AI representative of a human"

rather than:

"An AI form filler."

The browser automation is the actuator.

The LLM/VLM is part of the reasoning machinery.

The Digital Self is the persistent cognitive representation.

The Identity Graph is the structured memory.

The Verification Layer protects truth.

The Learning Engine makes the system improve.

The application executor turns cognition into action.

The central innovation is:

THE AGENT LEARNS HOW TO REPRESENT THE HUMAN,
NOT JUST HOW TO FILL THE FORM.

Build this as a real system.
