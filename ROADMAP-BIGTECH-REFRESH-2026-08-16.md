# Bigtech Refresh Roadmap — Claude Code

**Date:** 2026-08-16  
**Baseline:** `main` at `61c3ea4d9b5fcd75fb4feb9af7bbb020399d1eb6` (`0.2.0`)  
**Scope:** `/bigtech`, C-level and operational agents, hooks, model routing, backlog integration, CI and distribution.

This is the public, sanitized implementation roadmap. It deliberately excludes private machine paths, personal memories, private project names, session data and user-specific overlays.

## Primary goals

1. Make the plugin the single source of truth for the reusable bigtech core.
2. Stop using human headcount as a proxy for project complexity or risk.
3. Separate project `profile` from execution `capacity`.
4. Make `/bigtech` route by task and risk instead of activating organizational ceremony by default.
5. Give every agent a measurable role, route, tool policy and model tier.
6. Reduce repeated prompt boilerplate by using current Claude Code primitives.
7. Make model selection observable: requested model must match effective model.
8. Integrate `tab_pendencias` through one owner/versioned dependency path.
9. Move live distribution and CI to GitHub.
10. Add deterministic evals so releases prove behavior instead of counting commits.

---

# I. Historical failure mechanisms to eliminate

## 1. Dual authority

A reusable plugin core must not be independently maintained in both the plugin and user-level copies. User-level agents have higher precedence than plugin agents in Claude Code, so a local copy can silently shadow a newly released plugin agent.

**Target:** plugin owns reusable core; user/project scopes contain only intentional overlays or wrappers.

## 2. Headcount-driven classification

The current stack contains contradictory semantics: `/bigtech` still exposes `solo` as a project-size category while the Chief of Staff already states that one human maintainer must not automatically lower the project class.

**Target:** `solo` is capacity, never architecture/risk profile.

## 3. Reinforcement noise

Per-prompt C-suite reinforcement prevents context drift but can create management/process drift on trivial local tasks.

**Target:** compact session state plus intent-aware routing; no C-suite wake-up on every prompt.

## 4. Agent metadata without a semantic registry

Prompt files exist, but there is no single machine-readable registry proving reachability, ownership, model tier, tool policy and overlap.

**Target:** registry + semantic auditor in CI.

## 5. CI/distribution drift

The repository is hosted on GitHub but operational metadata and CI still contain Codeberg/Forgejo paths.

**Target:** GitHub Actions + GitHub release/install path; historical references may remain only when clearly historical.

---

# II. Target architecture

```text
User request
   |
   v
/bigtech main orchestrator
   |
   +--> CLASSIFY only when state is absent/stale
   |       -> profile + risk_axes + capacity
   |
   +--> ROUTE current task
   |       -> capability owner from registry
   |
   +--> EXECUTE
   |       -> minimum necessary agents
   |
   +--> VERIFY
   |       -> tests/evidence/independent verifier as risk requires
   |
   +--> RECHECK only on explicit triggers
           -> release, new consumer, schema/contract change, new regulation, etc.
```

## Project profile vs capacity

```text
PROFILE  = risk, complexity, governance and verification needed
CAPACITY = how much work can be executed in parallel
```

`capacity=solo` has zero weight in profile calculation.

### Profile dimensions

Score each dimension `0..3`, with evidence:

- criticality / cost of failure;
- blast radius;
- ecosystem coupling;
- reversibility;
- compliance / sensitive data;
- technical complexity;
- distribution / consumers;
- maintenance horizon.

Initial profile vocabulary:

- `lean` — low-risk, reversible, limited scope;
- `standard` — durable real product/repository with integrations;
- `critical` — high cost of error, sensitive data, multi-repo contracts or one-way doors;
- `enterprise` — genuinely systemic multi-product/multi-consumer scale or heavy governance/compliance.

Headcount does not promote or demote these profiles.

### Risk axes

A project may be standard overall but critical in one dimension:

```json
{
  "profile": "standard",
  "capacity": "solo",
  "risk_axes": {
    "security": "critical",
    "compliance": "critical",
    "delivery": "lean",
    "architecture": "standard"
  }
}
```

This prevents one critical axis from waking every corporate role.

---

# III. Implementation plan

## Phase 0 — Reproducible baseline

**Main:** **[Opus] 5 ou mais recente**  
**Mechanical collection:** **[Sonnet] 5 ou mais recente**

Measure, do not assume:

- exact agent count and filenames;
- model distribution;
- tool distribution;
- prompt sizes;
- skill and hook inventory;
- all agent references in skills/docs;
- current CI and release metadata;
- current Claude Code version and supported agent fields.

Create machine-readable baseline artifact.

**Done when:** no core file has been changed and the full baseline can be regenerated by one command.

## Phase 1 — Source-of-truth ADR

**Gate:** **[Fable] 5 ou mais recente**

Write an ADR that states:

- the plugin repository owns reusable core agents, skills, hooks and docs;
- user/project scopes may override only intentionally;
- no permanent bidirectional sync;
- personal overlays never become public product content automatically;
- every external component has one owner.

**Done when:** one owner exists for every reusable component and rollback is documented.

## Phase 2 — Classification redesign

**Planning:** **[Opus] 5 ou mais recente**  
**Implementation:** **[Sonnet] 5 ou mais recente**

Remove `solo` from architectural profile semantics in:

- `skills/bigtech/SKILL.md`;
- Chief of Staff prompt;
- hooks;
- docs;
- state marker.

Introduce schema v2, preferably `.bigtech.json`:

```json
{
  "schema": 2,
  "profile": "critical",
  "capacity": "solo",
  "risk_axes": {},
  "signals": {},
  "classified_at": "YYYY-MM-DD",
  "recheck_on": ["release", "new-consumer", "schema-change"]
}
```

Maintain read compatibility for the legacy marker during migration.

### Mandatory classification evals

1. trivial personal script -> `lean`;
2. one-maintainer multi-repo ecosystem -> at least `standard`;
3. one-maintainer health/PII application -> critical security/compliance axis;
4. large team + trivial low-risk site -> not `enterprise` merely from headcount.

Add hysteresis so marginal score changes do not thrash profile.

**Done when:** headcount has zero profile weight and all classification evals pass.

## Phase 3 — State-aware `/bigtech`

`/bigtech` becomes a router with four explicit operations:

```text
CLASSIFY -> ROUTE -> EXECUTE -> RECHECK
```

Classification is not recomputed on every request.

Chief of Staff output becomes compact:

```text
PROFILE
CAPACITY
RISK_AXES
ACTIVE_CAPABILITIES
DORMANT_CAPABILITIES
DEPENDENCY_ORDER
USER_DECISIONS
RECHECK_TRIGGERS
ANTI_OVERENGINEERING_REASON
```

A trivial bug in a critical project routes to the specialist and verifier; it does not reactivate the whole C-suite.

**Done when:** routing evals prove minimum-agent activation.

## Phase 4 — Hook redesign

Use current Claude Code lifecycle primitives.

### SessionStart

Inject only stable session facts:

- active profile/capacity;
- state path;
- docs root;
- compatibility warnings that are actually relevant.

### UserPromptSubmit

Inject task routing information only when the prompt changes routing state or explicitly invokes bigtech behavior.

Do not repeat a long corporate-mode reminder on every prompt.

### SubagentStart

Inject the minimum environment context into bigtech agents:

- docs root;
- profile/risk axes;
- current checkpoint;
- task-specific safety/authority facts.

Do not inject whole manuals; agents read only what their role requires.

### Memory/state

Do not turn on persistent per-agent `memory` for every agent as part of this migration. Keep static knowledge versioned; keep runtime state small, schema-versioned and recoverable.

**Done when:** hooks run once, trivial prompts receive no C-suite noise, and subagents obtain the required context without manual path boilerplate.

## Phase 5 — Agent registry and semantic audit

Create `config/agent-registry.json` or equivalent with at least:

```text
name
family
role
capabilities
routes
model_tier
effort
max_turns
write_mode
requires_bash
requires_web
docs_required
high_value_decisions
```

Create `scripts/audit_agents.py`.

Hard failures:

- duplicate agent name;
- registry entry without file;
- core agent file without registry entry;
- missing route target;
- multiple primary owners for the same capability;
- route cycle;
- invalid/deprecated tool configuration;
- agent references to missing agents;
- model policy violation.

Warnings requiring justification:

- prompt size beyond policy threshold;
- intentional role overlap;
- auto-discovery-only agent without an explicit orchestrator route.

### Ownership matrix

Each decision type has one primary owner. Examples:

| Work | Primary owner | Verifier/consulted |
|---|---|---|
| profile/capacity | Chief of Staff | risk specialists when required |
| product scope | CPO/PM | CTO for feasibility |
| cross-system architecture | CTO / software architect | CISO/tech lead as relevant |
| local implementation | specialist engineer | tech lead / QA |
| test strategy | QA | security/tech lead as relevant |
| audit | internal auditor | chapter specialists |
| cadence | flow/agile role only when actually needed | COO/EM |

**Done when:** every core agent is reachable and every primary capability has exactly one owner.

## Phase 6 — Agent prompt modernization

Remove generic boilerplate copied across dozens of agents. Each agent prompt should focus on:

```text
IDENTITY
MANDATE
NON-MANDATE
INPUTS
DECISIONS IT MAY TAKE
DECISIONS THAT ESCALATE
TOOLS
HANDOFF
DONE WHEN
ROLE-SPECIFIC ANTI-PATTERNS
```

Cross-cutting context belongs in docs, skills, hooks and registry.

### Least privilege

Advisory roles do not get shell/write access by default unless their deliverable requires it. Implementation roles get editing/build tools. Audit roles may inspect broadly but do not mutate production during an audit mandate.

**Done when:** `audit_agents.py` proves policy conformance and no capability is lost.

## Phase 7 — Model and effort policy

### Orchestration / strategic reasoning

Use **[Opus] 5 ou mais recente** selectively for:

- main orchestration;
- Chief of Staff;
- cross-system architecture;
- strategic C-level decisions;
- high-risk audits/reviews.

### Routine execution

Use **[Sonnet] 5 ou mais recente** by default for bounded implementation, QA execution, operational DevOps, documentation and mechanical refactoring.

Escalate a slice to **[Opus] 5 ou mais recente** only when evidence justifies it.

### Principal gates

Use **[Fable] 5 ou mais recente** rarely for:

- source-of-truth architecture;
- agent-governance redesign;
- classification rubric review;
- installation cutover;
- final adversarial audit.

### Effective-model proof

Model selection must account for Claude Code precedence:

```text
CLAUDE_CODE_SUBAGENT_MODEL
  > per-invocation override
  > agent frontmatter
  > main conversation model
```

Every model-routing eval records requested and effective model.

Do not invent unsupported invocation aliases. A principal-tier agent must use a technically supported full model ID/session path validated against the installed Claude Code version.

**Done when:** routine agents do not consume the strategic tier by default and effective-model evidence matches policy.

## Phase 8 — `tab_pendencias` ownership

Do not keep independent copies indefinitely.

Target:

- one upstream owner/version;
- versioned plugin dependency when the standalone component is packaged for it;
- temporary vendored copy must record upstream version/SHA and fail a drift check;
- individual agents send discoveries to the backlog owner instead of duplicating backlog logic.

**Done when:** one source of truth exists and drift is automatically detected.

## Phase 9 — GitHub CI and distribution

### Metadata

Update live repository/install URLs in manifest, marketplace metadata, README, AGENTS and support docs to GitHub. Historical changelog references may remain as history.

### GitHub Actions

Add `.github/workflows/ci.yml` using the same base scripts as local pre-CI.

Hard gates must include:

1. plugin validator;
2. semantic agent auditor;
3. hook tests;
4. manifest parse/schema;
5. version parity;
6. secret scan;
7. offline smoke;
8. deterministic routing/classification evals;
9. Claude plugin validation when part of release prerequisites.

Hard gates never turn “tool missing” into PASS.

### Migration order

```text
add GitHub CI
-> obtain a real green run
-> compare coverage with existing CI
-> enable branch protection / required check
-> only then remove obsolete Forgejo operational workflow
```

### Install/upgrade canary

In a clean Claude Code profile:

- install candidate;
- restart session;
- prove agents/skills/hooks are discovered;
- run behavior evals;
- upgrade from previous supported release;
- uninstall/reinstall;
- record CLI version, plugin SHA and results.

**Done when:** GitHub is the actual install/release/CI path and `main` is protected by required checks.

## Phase 10 — Behavioral eval suite

Create versioned real-world fixtures:

- trivial one-maintainer project;
- multi-repo one-maintainer ecosystem;
- sensitive-data one-maintainer project;
- trivial local fix inside critical project;
- cross-project contract change;
- product feature needing scope decision;
- release flow;
- user-scope agent shadowing plugin agent;
- model routing/effective model;
- final adversarial review.

Measure:

- route accuracy;
- number of unnecessary agents;
- turns/tokens;
- unnecessary user interruptions;
- contract failures;
- backlog churn;
- time to evidence.

**Done when:** regressions become permanent fixtures and model/profile/router changes cannot ship without passing them.

## Phase 11 — User-scope cutover

This phase applies to users who have legacy homonymous agents/hooks outside the plugin.

1. test plugin in a clean profile first;
2. classify local differences as reusable core vs intentional overlay;
3. port generic improvements to plugin;
4. remove/rename only the user-scope core copies that shadow plugin agents;
5. remove duplicate hook registrations;
6. keep personal-only agents/policies as overlay;
7. preserve rollback to last-known-good.

**Done when:** the plugin is the active source for core agents and hooks execute exactly once.

## Phase 12 — Release

Release checklist:

- source-of-truth audit green;
- agent semantic audit green;
- hook tests green;
- deterministic evals green;
- GitHub Actions green;
- manifest/marketplace version parity;
- clean install/upgrade canary;
- migration notes for `profile`/`capacity`;
- rollback test;
- immutable tag pointing to the audited SHA.

## Phase 13 — Final adversarial audit

**Gate:** **[Fable] 5 ou mais recente**

Attempt to prove the campaign is being declared complete too early.

Required questions:

1. Is any core plugin agent still unintentionally shadowed?
2. Can changing a plugin core agent be observed in a clean installation?
3. Does any core hook run twice?
4. Does human headcount still alter profile anywhere?
5. Does a one-maintainer multi-repo project classify correctly?
6. Does a trivial fix in a critical project avoid unnecessary C-suite activation?
7. Does every agent have a route or documented discovery-only role?
8. Are routine and strategic model tiers separated?
9. Is the **[Fable] 5 ou mais recente** path technically valid?
10. Are obsolete live Codeberg/Forgejo references gone?
11. Is GitHub CI actually required on `main`?
12. Does `tab_pendencias` have one owner?
13. Does a clean install reproduce the plugin behavior?
14. Was rollback tested?

No PASS without observable evidence.

---

# Parallelism policy

- main thread owns orchestration, validation and publication;
- subagents handle bounded slices;
- use `isolation: worktree` for parallel editing agents when file collision is possible;
- subagents do not recursively spawn subagents; nested workflow is chained by the main conversation;
- agent teams are optional and only useful where workers must communicate; they are not the default for independent code slices.

---

# Global Definition of Done — BIGTECH-REFRESH-COMPLETE

The refresh is complete only when all of these are true:

- reusable core has one source of truth;
- `solo` exists only as execution capacity, never project profile;
- profile is evidence-based and versioned;
- every core agent is registered, reachable and policy-compliant;
- every primary capability has one owner;
- routine work defaults to **[Sonnet] 5 ou mais recente**;
- strategic/orchestration work uses **[Opus] 5 ou mais recente** selectively;
- **[Fable] 5 ou mais recente** is restricted to explicit principal gates through a supported mechanism;
- requested and effective model can be audited;
- hook context is minimal and event-aware;
- no core hook runs twice;
- backlog integration has one owner;
- GitHub Actions is green and required;
- live metadata uses GitHub;
- clean install, upgrade and rollback tests pass;
- behavior evals pass;
- final adversarial audit passes.

Commit/release count is not a success metric. Only these counters and behavior proofs are.
