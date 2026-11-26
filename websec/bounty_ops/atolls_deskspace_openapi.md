# FINDING (VDP): Full OpenAPI spec + interactive docs publicly exposed
Target: api.deskspace.atolls.com (Atolls VDP — Intigriti)
Date: 2026-11-26 | Researcher: nellogem

## Evidence
GET https://api.deskspace.atolls.com/openapi.json → 200, 125KB
Full FastAPI schema: 85 endpoints incl. admin surface
(/api/admin/users, /audit-logs, /reports/*.csv, /sso/providers)
GET /docs → Swagger UI 200, /redoc → ReDoc 200

## Additional notes
- /auth/mock/login exists (POST, wants integer user_id)
  → prod returns 'Mock authentication is not enabled' (safe)
- user_id is INTEGER → if auth obtained, user IDs enumerable
- All data endpoints correctly return 401 unauthenticated

## Impact
Schema disclosure aids attacker recon (endpoint+param map of
entire admin API). Low severity info-disclosure for VDP.
Integer user IDs = latent IDOR risk if any endpoint leaks.
