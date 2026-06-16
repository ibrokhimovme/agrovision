# AgroVision — Git Branching Strategy

---

## Branch Structure

```
main           ← Production-ready code only. Protected. Requires PR + review.
develop        ← Integration branch. All features merge here first.
  └─ feature/<ticket>-<short-description>   ← Feature development
  └─ fix/<ticket>-<short-description>       ← Bug fixes
  └─ chore/<description>                    ← Tooling, deps, CI changes
  └─ docs/<description>                     ← Documentation only
  └─ refactor/<description>                 ← No behavior change
release/v{X.Y} ← Release preparation. Only bug fixes allowed.
hotfix/<desc>  ← Emergency fix on main. Backported to develop.
```

---

## Flow

1. Branch from `develop` for all feature work
2. Open PR to `develop` when ready
3. `develop` is merged to `main` only for releases via a release branch
4. Hotfixes branch from `main`, merge to both `main` and `develop`

---

## Branch Naming Examples

```
feature/AV-42-batch-vaccination-endpoint
fix/AV-101-login-lockout-not-resetting
chore/AV-55-upgrade-sqlalchemy-2-0
docs/AV-30-update-api-standards
refactor/AV-66-livestock-domain-models
release/v1.0
hotfix/fix-jwt-expiry-validation
```

---

## Protected Branch Rules

- `main`: require 1 review, passing CI, no direct push
- `develop`: require passing CI, no direct push

---

## PR Requirements

- Title references ticket number: `[AV-42] Add batch vaccination endpoint`
- Description explains why, not just what
- At least one reviewer approved
- All CI checks green
- No merge conflicts
