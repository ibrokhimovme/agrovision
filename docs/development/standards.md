# AgroVision — Development Standards

All contributors and future agents must follow these standards.
Deviations require justification in a PR description.

---

## Python (Backend Services)

### Style
- Python 3.12+
- Formatter: `ruff format` (double quotes, line length 100)
- Linter: `ruff check` (rules: E, F, I, N, W, UP)
- Type hints: required on all public functions and methods
- `from __future__ import annotations` at top of every module

### Architecture Layers (per service)
```
app/
  api/v1/          ← HTTP layer: routers, request/response schemas only
  application/     ← Use cases: orchestration, no business rules here
  domain/          ← Business logic, domain models, invariants
  infrastructure/  ← DB, messaging, cache adapters
  core/            ← Config, exceptions, constants
```

**Dependency rule:** api → application → domain ← infrastructure
- Domain layer has zero infrastructure dependencies
- Use abstract repository interfaces in domain layer
- Inject concrete implementations in infrastructure layer

### SQLAlchemy Models
- Always inherit `UUIDPrimaryKeyMixin` and `AuditMixin` from `shared.models.base`
- Use async sessions (`AsyncSession`) everywhere
- Never use `session.commit()` in domain layer — commit happens at application layer
- Use `mapped_column()` with explicit type annotations (SQLAlchemy 2.x style)

### Testing
- Every use case must have a unit test
- Integration tests use a real test database (never mock the DB — see feedback memory)
- Test file mirrors source path: `app/application/use_cases/authenticate.py` → `tests/unit/application/test_authenticate.py`
- Use `pytest-asyncio` for all async tests

---

## TypeScript (Frontend)

### Style
- TypeScript strict mode (`"strict": true`)
- Formatter: Prettier (configured via ESLint)
- No `any` types without explicit comment justification
- Props interfaces named `<ComponentName>Props`

### Architecture
```
src/
  components/      ← Reusable UI components (no business logic)
  pages/           ← Route-level components (compose components)
  hooks/           ← Custom React hooks (data fetching, business logic)
  services/        ← API client functions (thin wrappers around apiClient)
  store/           ← Zustand slices (global state)
  types/           ← TypeScript type definitions (mirror API contracts)
  utils/           ← Pure utility functions
```

### API calls
- All API calls go through `src/services/api.ts` — never use `fetch` directly
- Use `@tanstack/react-query` for data fetching in components
- Use Zustand for client-side state that survives navigation (auth, notifications)

### Form validation
- All forms use `react-hook-form` + `zod` schemas
- Zod schemas live alongside the form component in the same file or `schemas.ts` sibling

---

## Git

See `docs/development/git-workflow.md` for full branching strategy.
See `docs/development/commit-conventions.md` for commit message format.

---

## Security Checklist (Required Before PR Merge)

- [ ] No secrets in code or environment files committed
- [ ] All user inputs validated via Pydantic or Zod schema
- [ ] SQL queries use ORM (no raw string interpolation)
- [ ] File uploads validated (type, size)
- [ ] Authentication checked before any data access
- [ ] OWASP Top 10 considered for new endpoints
