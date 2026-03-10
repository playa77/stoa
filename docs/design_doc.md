# Design Document

## Project Working Title

**Canonical Agent Workbench**
*A human-directed platform for high-fidelity compression, analysis, deliberation, and action across information and real workspaces.*

---

## 1. Purpose

This project exists to give a human materially more cognitive leverage.

The core promise is not “chat with an AI.” The core promise is:

* take in a large amount of information,
* process it quickly,
* preserve fidelity to sources,
* reason across multiple frames or agents when useful,
* act on real files and environments,
* and leave behind inspectable traces, artifacts, and decisions.

The platform should feel like a cross between:

* a **workbench** for deliberate knowledge work,
* a **factory** for repeatable cognitive production,
* a **replicator** for turning raw inputs into usable artifacts,
* and a **wand** for giving a single operator disproportionate reach.

The user should emerge with better understanding, better outputs, and better control.

This is a platform for **meaningful compression and transformation of complexity**, not merely a conversational interface.

---

## 2. Executive Summary

The project will unify several existing lines of exploration into one canonical system:

* chat and operator UX,
* deep research and synthesis,
* multi-agent deliberation and adversarial review,
* local and remote workspace operations,
* and evaluation infrastructure beneath the product.

The result should be a single platform with two tightly connected layers:

### Top layer: the product

A human-facing agent workbench that supports:

* chat,
* research,
* deliberation,
* file and workspace operations,
* execution on local or remote environments,
* artifact creation and export,
* and replayable, inspectable runs.

### Bottom layer: the research spine

An evaluation and arena system that supports:

* repeatable benchmark tasks,
* side-by-side model and workflow comparison,
* tool-use evaluation,
* research quality evaluation,
* deliberation evaluation,
* and regression detection over time.

These two layers should not be separate worlds. The product should generate the exact traces and artifacts that the evaluation layer can score. The evaluation layer should continuously improve the product.

This creates a durable project with three strategic qualities at once:

* a **product**,
* a **protocol story**,
* and a **research spine**.

---

## 3. Problem Statement

Modern knowledge work has four persistent failures:

### 3.1 Information overload

Humans can gather more source material than they can meaningfully process. The bottleneck is no longer access; it is structured understanding.

### 3.2 Lossy synthesis

Most AI systems are very good at producing plausible summaries and much worse at preserving source fidelity, evidentiary structure, uncertainty, and provenance.

### 3.3 Fragmented workflows

Research, discussion, note-taking, file work, terminal work, and execution are usually split across disconnected tools. This fragments thought and weakens traceability.

### 3.4 Weak accountability

Most current agent systems are black boxes with poor observability. It is often difficult to see what happened, why it happened, what sources were used, what tool calls were made, and where the result can be trusted or challenged.

This project exists because a useful agent system must do more than generate language. It must help a human:

* think clearly,
* inspect the chain of work,
* preserve evidence,
* control execution,
* and improve workflows over time.

---

## 4. Product Vision

The platform is a **human-directed cognitive operations environment**.

The human remains the principal. The agents are not treated as mystical autonomous beings. They are instrumented cognitive machinery with useful roles, tools, constraints, traces, and bounded authority.

The system should allow one operator to do the work of a small, disciplined, evidence-conscious team.

The experience should support a spectrum of use cases:

* quickly understanding a large body of documents,
* generating source-grounded reports,
* comparing hypotheses or arguments,
* finding/identifying biases,
* finding/identifying rhetorical/sophistic devices/figures,
* finding/identifying inconsistencies and contradictions,
* running adversarial or multi-perspective review,
* operating on local files,
* operating on remote workspaces,
* producing deliverables,
* and replaying or auditing prior runs.

The product is not primarily for passive consumption. It is for **active intellectual and operational leverage**.

---

## 5. Design Principles

These principles should govern the entire system.

### 5.1 Human-first agency

The system amplifies human judgment; it does not replace it. Human review, intervention, steering, and override are first-class.

### 5.2 Fidelity over fluency

A polished lie is worse than a rough truth. When there is tension between elegance and evidentiary accuracy, accuracy wins.

### 5.3 Sources are sacred

Sources, citations, provenance, and uncertainty must be treated as core product features, not garnish.

### 5.4 Trace everything that matters

A serious run should be inspectable: active skills, tool calls, outputs, citations, artifacts, failures, retries, decisions, and timing.

### 5.5 Tools over theatrics

“Multi-agent” is only justified when it yields measurable gains in quality, robustness, or clarity. Persona theater is not a feature.

### 5.6 Skills, not monolithic system prompts

Inside the agentic runtime, durable behavioral guidance, role definitions, tool guidance, and workflow control should be expressed as **Claude Skills standard skill documents**, using the same skills format/standard that OpenClaw uses.

The platform should **not** rely on old-style monolithic hidden “system prompts” or ad hoc “system instructions” as its primary internal control surface. User-facing user input may still be colloquially called a prompt when appropriate, but internally the machine should think in terms of **skills, skill packs, workflow policies, and resolved control assets**.

### 5.7 Modular, protocol-oriented architecture

The platform should treat models, tools, servers, and workflows as replaceable modules connected through stable interfaces.

### 5.8 Local-first where sensible, remote-capable where necessary

Users should have strong local control, but the system must also operate meaningfully across remote environments and cloud-connected tools.

### 5.9 Evaluation is part of the product

A platform that cannot measure improvement will drift into vibes. Evaluation must be built into the architecture from the start.

### 5.10 Safe execution by default

Action-capable agents must be constrained, reviewable, and reversible where possible.

### 5.11 Aesthetic coherence matters

The interface should feel powerful, distinctive, and intentional. It should not look like a generic corporate chat shell wearing fake glasses.

---

## 6. Strategic Thesis

The strategic thesis is:

> The frontier is not just better models. The frontier is better *systems around models*: better interfaces, better protocols, better traceability, better tool integration, better evaluation, and better human control.

This project should therefore avoid becoming merely another thin model wrapper.

Its defensible value should come from:

* workflow design,
* architectural integration,
* provenance and replay,
* strong operator UX,
* protocol fluency,
* and evaluation infrastructure.

The system should remain useful even as model providers, APIs, and model rankings change.

---

## 7. Core User Promise

A user should be able to say, in effect:

* “Here is a large messy body of information.”
* “Help me compress it without distorting it.”
* “Challenge the result from multiple serious perspectives.”
* “Show me exactly where the claims came from.”
* “Turn the result into a useful artifact.”
* “Then act on the relevant files or workspace carefully.”
* “And let me replay or audit the whole process later.”

If the platform consistently delivers this, it will be genuinely valuable.

---

## 8. Scope

### 8.1 In scope

The canonical system should ultimately support:

#### A. Conversational orchestration

* rich chat as an entry point,
* branching sessions,
* saved runs,
* model and workflow selection,
* user control over tools and permissions.

#### B. Research and synthesis

* source ingestion,
* retrieval across documents and files,
* citation-aware synthesis,
* source-linked claims,
* structured report generation,
* exportable deliverables.

#### C. Deliberation

* multi-perspective reasoning,
* adversarial review,
* finding/identifying biases,
* finding/identifying rhetorical/sophistic devices/figures,
* finding/identifying inconsistencies and contradictions,
* critique and revision loops,
* ranking of options or hypotheses,
* explicit confidence and disagreement surfaces.

#### D. Workspace operations

* local file access,
* remote file access,
* structured editing,
* patch application,
* version-aware actions,
* terminal or command execution under constraints.

#### E. Run trace and audit

* event timelines,
* tool call logs,
* artifact lineage,
* citations and evidence maps,
* replay and inspection.

#### F. Evaluation and arena

* benchmark tasks,
* scoring,
* side-by-side comparisons,
* regression tracking,
* workflow evaluation,
* model and tool-routing evaluation.

### 8.2 Out of scope, at least initially

To keep the project coherent, the following should not be treated as first-wave priorities:

* mass-market social features,
* general-purpose autonomous agents operating without strong constraints,
* app-store style ecosystem complexity before the core platform is stable,
* broad enterprise bureaucracy features before the single-user or small-team experience is excellent,
* gimmicky avatars or agent personalities that do not improve outcomes,
* speculative hardware integrations.

The first goal is not empire. It is a hard, coherent core.

---

## 9. Target Users

The primary target user is a **serious operator dealing with complexity**.

This may include:

* researchers,
* analysts,
* technical generalists,
* writers,
* investigators,
* founders,
* engineers,
* consultants,
* and high-agency individuals who routinely convert messy inputs into consequential outputs.

These users value:

* speed,
* evidence,
* control,
* iteration,
* auditability,
* and leverage.

They do not merely want conversation. They want **cognitive throughput with guardrails**.

---

## 10. User Archetypes

### 10.1 The Research Operator

Needs to gather, ingest, compare, compress, and report across many sources without losing citations or nuance.

### 10.2 The Builder-Operator

Needs to work with local and remote files, codebases, terminals, and generated artifacts while keeping an AI agent under disciplined control.

### 10.3 The Decision Analyst

Needs multiple frames, adversarial review, option ranking, and explicit uncertainty before making a consequential decision.

### 10.4 The Evaluator

Needs to compare models, skill packs, workflows, and tools under repeatable conditions and see what actually improves outcomes.

These are not separate products. They are roles the same power-user may inhabit across the day.

---

## 11. Conceptual Model

The platform should be understood as five layers.

### 11.1 Interaction layer

The visible interface where the user works:

* chat,
* tabs or sessions,
* documents,
* run views,
* trace panels,
* file browser,
* workspace tools,
* comparison views.

### 11.2 Orchestration layer

The runtime that manages:

* workflows,
* skill resolution and loading,
* tool permissions,
* agent roles,
* routing,
* retries,
* state,
* checkpoints,
* and handoffs.

### 11.3 Capability layer

The actual things the system can do:

* retrieval,
* search,
* reasoning passes,
* deliberation,
* file operations,
* execution,
* exports,
* scoring.

### 11.4 Protocol layer

The standardized connection surfaces for models, tool servers, and external systems.

### 11.5 Evaluation layer

The shared substrate for measurement, replay, comparison, and improvement.

This separation is important. Without it, the system becomes a pile of fused hacks. With it, the platform can evolve intelligently.

---

## 12. Product Pillars

The product should be built around four visible pillars and one hidden pillar.

### 12.1 Pillar 1: Research

The platform must excel at ingesting and compressing information with high source fidelity.

The user should be able to move from raw material to:

* notes,
* briefs,
* reports,
* maps of claims and evidence,
* and structured outputs.

### 12.2 Pillar 2: Deliberation

The platform must be able to improve thinking quality through structured internal disagreement.

That means:

* contrasting frames,
* adversarial critique,
* formal scrutiny,
* alternative hypotheses,
* devil’s advocate pressure,
* and forced justification.

### 12.3 Pillar 3: Action

The platform must connect thought to real work.

That means:

* file operations,
* remote workspace access,
* patch proposals,
* command execution,
* artifact creation,
* and export.

### 12.4 Pillar 4: Operator Control

The user must be able to see, steer, approve, interrupt, constrain, and replay what the system is doing.

### 12.5 Hidden pillar: Evaluation

Everything above should be measurable.

---

## 13. Modes of Operation

The workbench should eventually expose several first-class modes, even if the implementation begins with only a subset.

### 13.1 Chat mode

Fast entry point for asking, steering, iterating, and invoking workflows.

### 13.2 Research mode

Document-focused ingestion, retrieval, source inspection, synthesis, and export.

### 13.3 Deliberation mode

Structured multi-agent or multi-frame reasoning where the output is more than a monologue.

### 13.4 Workspace mode

Local and remote file browsing, diffing, editing, patching, execution, and artifact handling.

### 13.5 Arena mode

Side-by-side comparison of models, skill packs, workflows, or strategies on defined tasks.

### 13.6 Replay mode

Inspection of prior runs, evidence maps, timelines, tool calls, failures, and outputs.

These modes should feel like parts of one machine, not like separate apps awkwardly sharing a coat.

---

## 14. Key User Journeys

### 14.1 Research-to-report journey

1. User imports or points to a corpus.
2. System ingests and indexes material.
3. User asks a question or defines an output goal.
4. System retrieves relevant material.
5. System synthesizes with citations and uncertainty markers.
6. User optionally invokes deliberation or adversarial review.
7. System revises output.
8. User exports a report or artifact.
9. Full run remains inspectable and replayable.

### 14.2 Question-to-deliberation journey

1. User presents a difficult question or decision.
2. System creates structured reasoning roles or frames.
3. Arguments, critiques, formal/rhetorical analysis, and revisions are generated.
4. Evidence is surfaced.
5. Points of agreement, disagreement and formal/rhetorical interest are made explicit.
6. Final synthesis is produced.
7. User can inspect the full deliberation trace.

### 14.3 Task-to-action journey

1. User specifies a real workspace task.
2. System explores relevant local or remote files.
3. System proposes changes.
4. User reviews and approves.
5. System applies patches or executes commands under constraints.
6. Results and artifacts are logged.
7. User can roll back, inspect, or iterate.

### 14.4 Evaluation journey

1. User defines or selects tasks.
2. System runs multiple model or workflow variants.
3. Outputs, traces, timings, and artifacts are captured.
4. Scoring is applied.
5. Results are compared.
6. Regressions or gains are visible over time.

---

## 15. Differentiation

The project should differentiate itself in the following ways.

### 15.1 Evidence-centric design

Most AI interfaces optimize for fluid conversation. This platform should optimize for evidence-conscious work.

### 15.2 Unified cognition-to-action loop

Most products stop at text. This one should reach into files, workspaces, execution, and artifact production.

### 15.3 Deliberation with purpose

Multi-agent structures should exist to improve outcomes, not to produce decorative chatter.

### 15.4 Replayable intelligence

A run should be something you can inspect like a build pipeline or lab procedure, not a disappearing magic trick.

### 15.5 Product plus eval spine

The same system that helps perform work should also help measure and improve how that work is performed.

---

## 16. Non-Functional Product Goals

The product should aim for the following qualities.

### 16.1 Trustworthiness

Users should be able to inspect why an output exists.

### 16.2 Modularity

Model providers, tools, servers, and workflows should be replaceable.

### 16.3 Extensibility

New capabilities should be addable without architectural surgery.

### 16.4 Performance transparency

Long or complex runs should expose progress and state rather than becoming silent voids.

### 16.5 Robustness

Failures should degrade gracefully, surface clearly, and remain debuggable.

### 16.6 Operator delight

The system should feel powerful, coherent, and a little dangerous in the good way—like precision machinery, not office sludge.

---

## 17. Safety and Control Philosophy

This platform will increasingly bridge reasoning and action. Therefore, safety must be built into the operator model.

The system should assume:

* read access is cheaper than write access,
* proposal is cheaper than execution,
* simulation is cheaper than mutation,
* explicit human approval is required for higher-risk actions,
* actions must be logged,
* and destructive operations require elevated friction.

The goal is not sterile restriction. The goal is **confidently usable power**.

---

## 18. Relationship Between Product and Evaluation Layer

The evaluation layer is not a separate analytics afterthought. It is a first-class counterpart.

Every major workflow in the product should, where feasible, emit structured data that can feed evaluation:

* task definition,
* inputs,
* retrieved evidence,
* active skills, workflow policies, or other control assets,
* intermediate outputs,
* tool calls,
* timings,
* final artifacts,
* and scored outcomes.

This has several benefits:

* faster iteration,
* regression detection,
* better model routing,
* workflow comparison,
* and a path from anecdotal improvement to measurable improvement.

A system that works but cannot learn from itself is unfinished.

---

## 19. Relationship to Existing Repositories

This project should be treated as a convergence point for the strongest elements already explored.

### From chat-oriented products

Take:

* session management,
* streaming,
* branching history,
* packaging discipline,
* user-facing polish.

### From research systems

Take:

* retrieval,
* report generation,
* structured workflows,
* export,
* evidence handling.

### From multi-agent systems

Take:

* structured roles,
* debate and critique,
* director models,
* reasoning trace surfaces,
* comparison mechanisms.

### From workspace/operator tools

Take:

* terminal integration,
* remote environment connectivity,
* file operations,
* operator-centric workflow.

### From games or arena concepts

Take:

* side-by-side comparison,
* scoring,
* benchmarking,
* and controlled competition between strategies.

The purpose is not to merge codebases mechanically. The purpose is to merge their strongest ideas into one architecture.

---

## 20. Product Boundaries and Discipline

To keep the project healthy, several traps should be avoided.

### 20.1 Do not mistake interface multiplicity for platform progress

Five overlapping shells do not equal one mature platform.

### 20.2 Do not confuse more agents with better outcomes

Additional roles are only justified when they improve measurable quality.

### 20.3 Do not let protocols become ideology

Protocol support matters because it reduces lock-in and improves interoperability. It is a means, not a religion.

### 20.4 Do not build enterprise theater too early

Permissions matrices, organization dashboards, and administrative scaffolding can wait until the single-user power case is excellent.

### 20.5 Do not let polish outrun architecture

A beautiful shell around brittle internals is still brittle. Lipstick on a pipeline pig is still a pig.

---

## 21. Product Success Criteria

The product should eventually be considered successful if it can reliably demonstrate the following.

### 21.1 Compression with fidelity

Given a complex source body, the system can produce useful syntheses without severe source distortion.

### 21.2 Deliberation that improves outcomes

Structured critique or multi-perspective reasoning produces better outputs than single-pass generation on meaningful tasks.

### 21.3 Action with control

The system can move from analysis to safe, inspectable file or workspace operations.

### 21.4 Replayable and auditable runs

Users can inspect how results were produced.

### 21.5 Measurable iteration

Changes to models, skills, tools, or workflows can be evaluated rather than guessed at.

### 21.6 Coherent user experience

The platform feels like one machine with multiple modes, not a family of cousins arguing at a reunion.

---

## 22. First-Order Strategic Decisions

The following decisions should be treated as foundational.

### 22.1 This is a platform, not a single-feature app

It should be designed for composable workflows and extensible capabilities.

### 22.2 The human is the operator of record

Even where automation is strong, control remains explicit.

### 22.3 Traceability is mandatory

Runs that matter must be inspectable.

### 22.4 Evaluation is built in from the start

Not bolted on after the architecture calcifies.

### 22.5 The system should be protocol-friendly and provider-agnostic

It should survive model churn.

### 22.6 Workspace interaction is a first-class capability

Not an afterthought beside chat and research.

### 22.7 Internal control is skills-based

Inside the agentic system, reusable behavioral and workflow guidance must be represented as Claude Skills standard skill documents, aligned with the same format/standard used by OpenClaw. The architecture should avoid falling back to old-style monolithic system-prompt design except where an external provider API makes some minimal wrapper unavoidable.

---

## 23. Product Personality and Feel

The product should feel:

* precise,
* capable,
* operator-grade,
* exploratory,
* and slightly arcane in a satisfying way.

Not whimsical. Not corporate. Not toy-like. Not sterile.

It should feel like a serious instrument that happens to be beautiful.

The right emotional note is something like:

* a laboratory,
* a command deck,
* a scholar’s machine,
* and a workshop for controlled intellectual force.

---

## 24. Naming Direction

A final name is not required yet, but the name should fit the actual strategic identity.

It should suggest some combination of:

* knowledge compression,
* transformation,
* instrumentation,
* agency,
* synthesis,
* or controlled power.

It should not sound like:

* a generic SaaS chatbot,
* a toy assistant,
* a sterile enterprise platform,
* or a random fantasy noun disconnected from function.

The name has to deserve the machine.

---

## 25. Recommended Document Set

The proposed three-document method is correct and should be adopted.

The roles of the documents should be:

### 25.1 Design Document

Defines:

* vision,
* purpose,
* product boundaries,
* user promise,
* design principles,
* strategic logic,
* and what kind of machine this is.

### 25.2 Technical Specification

Defines:

* system architecture,
* modules,
* data models,
* interfaces,
* state flows,
* protocols,
* permissions,
* storage,
* workflows,
* skill resolution and precedence,
* skill-pack composition,
* error handling,
* testing surfaces,
* and implementation constraints.

### 25.3 Atomic Roadmap

Defines:

* implementation order,
* dependency graph,
* milestone structure,
* exact work packages,
* acceptance criteria,
* file-level expectations,
* test expectations,
* and what a less capable implementation agent must do step by step.

The roadmap is the execution spine. If the roadmap is weak, the project will dissolve into intelligent flailing.

---

## 26. One Improvement to the Method

The three documents are the right core. One addition should be embedded across them:

### Decision discipline

Every major architectural or product choice should have:

* rationale,
* alternatives considered,
* tradeoffs,
* and downstream consequences.

This does **not** require a fourth standalone document yet. It can be handled as explicit decision sections inside the technical specification and roadmap.

That way, smaller models do not merely follow execution steps blindly; they also inherit the reasons those steps exist.

---

## 27. Final Position

Yes, this is the correct approach.

For a project of this scope, writing the design document, the comprehensive technical specification, and the atomic roadmap before implementation is not bureaucracy. It is structural sanity.

Without these documents, the project risks becoming:

* a pile of overlapping prototypes,
* a vague platform dream,
* or an architecture shaped by whatever implementation model happened to improvise that day.

With them, the project has a real chance to become a coherent machine.

This design document therefore establishes the top-level identity of the project:

> A human-directed agent workbench and evaluation platform for high-fidelity compression, analysis, deliberation, and action across information and real workspaces.

That is the machine we are building.
