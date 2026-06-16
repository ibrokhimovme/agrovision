# AgroVision — API Standards

All REST APIs across all 8 services must conform to these standards.
Deviations require a recorded ADR.

---

## URL Conventions

```
/api/v1/{resource}                         # Collection
/api/v1/{resource}/{id}                    # Single resource
/api/v1/{resource}/{id}/{sub-resource}     # Nested resource
```

**Rules:**
- Use kebab-case for multi-word resources: `/health-records`, `/stock-items`
- Always include `/api/v1` prefix (versioning)
- Resource names are plural nouns: `/farms`, `/batches`, `/users`
- Actions that don't map to CRUD use POST with a verb suffix: `/batches/{id}/close`, `/users/{id}/lock`

---

## HTTP Methods

| Method | Usage |
|--------|-------|
| `GET` | Read one or list (never mutates state) |
| `POST` | Create new resource |
| `PUT` | Full update (replace entire resource) |
| `PATCH` | Partial update (only provided fields) |
| `DELETE` | Soft delete (sets deleted_at, never hard deletes) |

---

## Response Envelope

### Success — single resource
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human-readable note"
}
```

### Success — list/paginated
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 142,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

### Error
```json
{
  "success": false,
  "error_code": "NOT_FOUND",
  "message": "Batch with id '...' was not found.",
  "details": null,
  "trace_id": "req-uuid"
}
```

### Validation Error
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "Invalid email format", "code": "invalid_email" }
  ]
}
```

---

## Pagination

All list endpoints accept:
- `page` (integer, 1-based, default: 1)
- `page_size` (integer, 1-100, default: 20)

Example: `GET /api/v1/batches?page=2&page_size=50`

---

## Filtering and Sorting

- Filters as query params: `?farm_id=...&status=active&species=broiler`
- Sorting: `?sort=created_at&order=desc`
- Date range: `?from=2026-01-01&to=2026-06-30`

---

## HTTP Status Codes

| Code | When |
|------|------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no body) |
| 400 | Bad request (malformed JSON, missing required field) |
| 401 | Missing or invalid token |
| 403 | Valid token but insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate, invalid state transition) |
| 422 | Validation failed (field-level errors) |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error |
| 503 | Service temporarily unavailable |

---

## Versioning Strategy

- Current version: `v1`
- Breaking changes (field removal, type change, semantic change): bump to `v2`
- Non-breaking additions (new optional fields, new endpoints): stays `v1`
- Old versions supported for minimum 6 months after new version release
- Deprecation communicated via `Deprecation` and `Sunset` response headers

---

## Date and Time

- All timestamps in ISO 8601 UTC: `"2026-06-16T12:00:00Z"`
- Never return naive datetimes (no timezone)
- Clients must send UTC for write operations

---

## Field Naming

- JSON fields: `snake_case`
- UUIDs: string representation `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`
- Monetary amounts: string decimals `"125000.00"` (avoid float precision issues)
- Enums: lowercase string values `"active"`, `"quarantine"`
