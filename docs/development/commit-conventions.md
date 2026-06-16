# AgroVision — Commit Message Conventions

Uses Conventional Commits (https://www.conventionalcommits.org/).

---

## Format

```
<type>(<scope>): <short description>

[optional body — explain WHY, not WHAT]

[optional footer: BREAKING CHANGE, Refs, Closes]
```

---

## Types

| Type | When to Use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Build process, dependencies, CI |
| `perf` | Performance improvement |
| `ci` | CI/CD configuration changes |
| `arch` | Architectural change (ADR must be updated first) |

---

## Scopes

Use the service or layer name:
`identity`, `farm`, `livestock`, `inventory`, `finance`, `notification`, `reporting`, `gateway`, `frontend`, `shared`, `infra`, `docs`, `governance`

---

## Examples

```
feat(livestock): add batch quarantine-to-active state transition

Implements BP-03 quarantine release flow. Validates minimum quarantine
duration before allowing transition. Publishes BatchOpenedEvent on success.

Refs: SRS §5.3, BRD §9.3
```

```
fix(identity): reset failed login counter after successful auth

Counter was not reset on success, causing false lockouts on subsequent
failures after a successful login.

Closes: AV-88
```

```
arch(infra): switch from monolith to microservices baseline

Records ADR-002 superseding ADR-001. All service boundaries established.
See docs/decisions/ADR-002.md.
```

```
feat(inventory): enforce FIFO dispatch order on stock movements

Implements BP-09 FIFO/FEFO rule. StockBatch.is_expired blocks dispatch
of expired lots. Domain layer raises BusinessRuleViolationError on attempt.
```

---

## Rules

- Subject line ≤72 characters
- Present tense: "add" not "added" or "adds"
- No period at end of subject line
- Body lines ≤100 characters
- Breaking changes: `BREAKING CHANGE:` in footer
- Reference BRD/SRS sections in commit body for feature commits
