# AgroVision — Implementation Rules
**Authority:** This document governs all development execution. All agents, sessions, and developers must comply.  
**Version:** 1.0 | **Created:** 2026-06-16 | **Status:** ACTIVE

---

## 1. The Golden Rule

> **The repository is the truth. project_state.md is the map. Status labels alone are never trusted.**

No phase is considered complete because a document says COMPLETED.  
A phase is VERIFIED_COMPLETE only when implementation evidence exists in the repository.

---

## 2. Session Start Protocol

Every new session, agent, or conversation MUST execute this sequence before any work:

```
1. READ  .project-governance/project_state.md
2. READ  .project-governance/project_memory.md
3. READ  .project-governance/execution/phase_status.md
4. READ  .project-governance/execution/master_roadmap.md
5. INSPECT repository structure relevant to current phase
6. VERIFY phase status through code inspection (not labels)
7. DETERMINE next unfinished task
8. REPORT current state to user before acting
```

**Never skip this protocol.** It takes seconds. Skipping it wastes hours.

---

## 3. Phase Execution Protocol

When user says **"Execute Phase X"** or **"Build Phase X"** or **"Implement Phase X"**:

```
STEP 1 — DISCOVERY
  Read project_state.md → check recorded status for Phase X
  Inspect repository → verify actual implementation state
  
STEP 2 — CLASSIFICATION
  IF phase is VERIFIED_COMPLETE:
    Report: "Phase X is already verified complete."
    Show evidence. Ask: "Proceed to Phase X+1?"
    
  IF phase is IN_PROGRESS (partial):
    Run gap analysis against master_roadmap.md deliverables
    List: what exists vs. what is missing
    Implement only the missing items
    
  IF phase is NOT_STARTED:
    Verify all dependencies (prior phases) are VERIFIED_COMPLETE
    If dependencies not met → report BLOCKED, do not proceed
    If dependencies met → create implementation plan → execute

STEP 3 — IMPLEMENTATION
  Follow task order in development_backlog.md for this phase
  Complete one task fully before starting next
  Update phase_status.md after each task completion

STEP 4 — VERIFICATION
  Run verification checklist from project_state.md for this phase
  All checklist items must pass
  Record evidence (file paths, test results)

STEP 5 — COMPLETION
  Update project_state.md → mark phase VERIFIED_COMPLETE
  Update phase_status.md → mark phase COMPLETED
  Update development_backlog.md → mark all tasks COMPLETED
  Append to project_memory.md Change History
  Report: implementation summary, files changed, requirements satisfied
```

---

## 4. "Continue" Command Protocol

When user says **"Continue"**:

```
1. Read project_state.md → find current active phase
2. Find first task with status IN_PROGRESS or NOT_STARTED in that phase
3. Verify dependencies for that task
4. Execute task
5. Update tracking documents
6. Report result
7. Ask: "Continue to next task?" or proceed if in autonomous mode
```

---

## 5. "Show Status" Command Protocol

When user says **"Show Status"**:

```
Generate from REPOSITORY INSPECTION, not from stored labels:

─── PROJECT STATUS REPORT ────────────────────────
Date: [current date]
Active Phase: [phase name and number]
Overall Progress: [X / 16 phases]

VERIFIED COMPLETE phases:
  [list with completion dates]

IN PROGRESS phases:
  [list with current task]

NOT STARTED phases:
  [list]

BLOCKED items:
  [list with blocking reason]

Next action: [specific next task]
────────────────────────────────────────────────
```

---

## 6. Alignment Verification (Before Any Code)

Before writing any implementation code, verify:

| Check | Source | Rule |
|-------|--------|------|
| BRD alignment | `project_memory.md §3` | Feature must be in BRD §6.1 scope |
| SRS alignment | `project_memory.md §6` | Feature must reference a SF-XX or FR-XXX |
| ADR alignment | `project_memory.md §12` | Implementation must follow ADR-002 architecture |
| MVP scope | `project_memory.md §21` | Feature must be in MVP scope per ADR-003 |
| Phase dependency | `master_roadmap.md` | Prior phase must be VERIFIED_COMPLETE |
| Service boundary | `docs/architecture/service-ownership.md` | Feature goes in correct service |

If any check fails → STOP. Report the conflict. Do not implement.

---

## 7. MVP Scope Protection

The MVP scope is defined in ADR-003 and `project_memory.md §21–25`.

```
IF a requested feature is outside MVP scope:
  Mark it: FUTURE_RELEASE
  Do NOT implement it
  Record it in development_backlog.md under DEFERRED section
  Report to user: "Feature X is outside MVP scope (ADR-003). Marked FUTURE_RELEASE."
```

MVP boundary enforcement:
- Individual animal tracking → FUTURE_RELEASE
- Cattle / sheep / goat → FUTURE_RELEASE
- Email / SMS notifications → FUTURE_RELEASE (Phase 2)
- Slaughter as separate module → FUTURE_RELEASE
- Advanced debtor/creditor AR → FUTURE_RELEASE
- Transport management → FUTURE_RELEASE
- Government compliance workflow → FUTURE_RELEASE

---

## 8. Architecture Rules (ADR-002)

All implementation must follow these non-negotiable rules:

```
LAYERING (per service):
  api/           → HTTP handlers, request/response DTOs, no business logic
  application/   → use cases, orchestration, no DB access
  domain/        → models, repository interfaces, domain services, no infrastructure
  infrastructure → DB sessions, repository implementations, message publishers

CROSS-SERVICE:
  Services communicate via: REST API (sync) OR RabbitMQ events (async)
  NEVER via: shared database, direct function import, shared memory
  
DATABASE:
  Each service has ONE database
  No cross-service DB queries EVER
  
JWT:
  Verified ONLY at api-gateway
  Downstream services trust X-User-Id and X-User-Roles headers
  
EVENTS:
  Exchange: agrovision.events (topic)
  Routing key: {domain}.{entity}.{action}
  All events are immutable (frozen Pydantic models)
  Only publish MVP events (see shared/events/schemas.py MVP section)
```

---

## 9. Code Quality Standards

```
MIGRATIONS:
  Every model change requires an Alembic migration
  Migration must be reversible (upgrade + downgrade)
  Never modify existing migration files — create new ones

TESTS:
  Every use case requires at least one unit test
  Every API endpoint requires at least one integration test
  Tests live in: services/{service}/tests/unit/ or tests/integration/

API STANDARDS:
  All responses use APIResponse envelope from shared/contracts/api_standards.py
  Pagination uses PaginatedResponse for list endpoints
  Errors use ErrorResponse with code + message
  All endpoints versioned at /api/v1/

NAMING:
  Follow existing patterns in domain models and use cases
  Uzbek domain terminology in comments where appropriate (BRD §4)
```

---

## 10. Tracking Discipline

After EVERY completed task, update ALL of these:

| File | What to update |
|------|---------------|
| `project_state.md` | Phase verification record, change ledger entry |
| `phase_status.md` | Task status → COMPLETED, phase progress % |
| `development_backlog.md` | Task status → COMPLETED, completion date |
| `project_memory.md` | Change History (CH-XXX entry), Development Progress table |

**Never batch updates.** Update immediately after each task.

---

## 11. Forbidden Actions

```
NEVER:
  - Skip session start protocol
  - Mark a phase VERIFIED_COMPLETE without code inspection
  - Implement features from future phases without approval
  - Cross service database boundaries
  - Modify existing Alembic migration files
  - Skip JWT verification at api-gateway
  - Implement FUTURE_RELEASE features without explicit user approval
  - Delete Change History entries (append only)
  - Implement without BRD/SRS traceability
  - Add AI attribution metadata to commit messages (see §13)
```

---

## 13. Git Attribution Policy

**This policy is permanent and non-negotiable.**

### 13.1 Prohibited Metadata

The following are permanently forbidden in all commit messages, PR descriptions, and repository files:

- `Co-Authored-By` / `Co-authored-by`
- `Generated-By` / `Generated-by`
- `Created-By` / `Created-by`
- `Authored-By` / `Authored-by`
- Any reference to: Claude, Anthropic, AI Assistant, AI Generated, Bot Attribution

### 13.2 Commit Message Format

All commit messages must be single-line:

```
git commit -m "meaningful description of the change"
```

- No multi-line trailers
- No metadata blocks
- No attribution signatures
- No co-author information

### 13.3 Repository Ownership

Repository ownership belongs exclusively to the repository owner (ibrokhimovme). No external contributor attribution is permitted unless explicitly configured by the repository owner.

### 13.4 Agent / Tool Compliance

Any agent, assistant, script, or automation tool that generates commit recommendations for this repository must:

1. Produce only single-line `git commit -m "..."` commands
2. Include no trailers of any kind
3. Include no attribution metadata of any kind
4. Never add Co-Authored-By or similar lines regardless of default behavior

---

## 12. Phase Dependency Map

```
Phase 0 (Repository Validation)
  └→ Phase 1 (Runtime Readiness)
       └→ Phase 2 (Identity Service)
            ├→ Phase 3 (Frontend Foundation)
            │    └→ [all frontend phases]
            └→ Phase 4 (Poultry Batch Management)
                 ├→ Phase 5 (Feed Consumption)
                 │    └→ Phase 10 (Cost Tracking)
                 ├→ Phase 6 (Mortality Tracking)
                 ├→ Phase 7 (Vaccination Management)
                 │    └→ Phase 9 (Inventory Integration)
                 ├→ Phase 8 (Weight Sampling)
                 └→ Phase 9 (Inventory Integration)
                      └→ Phase 10 (Cost Tracking)
                           └→ Phase 11 (Sales Management)
                                └→ Phase 12 (Profit Analysis)
                                     ├→ Phase 13 (Notifications)
                                     ├→ Phase 14 (Reporting)
                                     └→ Phase 15 (MVP Stabilization)
```

---

*Implementation Rules v1.0 — AgroVision Engineering Governance*  
*Last updated: 2026-06-16*
