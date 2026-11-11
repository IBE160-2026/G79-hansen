# Final current-technology review — 2026-11-11

**Verdict: PASS for architecture/story planning, with implementation gates retained.** No blocking false vendor capability or invalid version claim found. This is an independent document/source review, not an install, SDK compatibility test, security test, or deployment.

## Evidence and fit

| Area | Official evidence | Assessment |
| --- | --- | --- |
| FastAPI seed | [Maintainer package](https://pypi.org/project/fastapi/), [static serving](https://fastapi.tiangolo.com/tutorial/static-files/) | 0.162.4 is published 10 November 2026. Serving public files and JSON API through one application is supported. The researched seed is explicitly subject to a tested implementation lockfile. |
| PDF candidate | [Maintainer package](https://pypi.org/project/pypdf/), [extraction guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | 7.0.1 is published 10 November 2026. Per-page text extraction is suitable for the bounded experiment. The document correctly excludes OCR and does not treat count/byte limits as a complete memory safeguard. Library adoption remains experiment-gated. |
| Server login | [Supabase advanced server guidance](https://supabase.com/docs/guides/auth/server-side/advanced-guide), [Python sign-out](https://supabase.com/docs/reference/python/auth-signout) | The standard browser-SDK SSR explanation expects browser access to refresh credentials. The spine deliberately uses a different backend-for-frontend boundary: browser receives only an opaque application identifier while provider credentials stay on the server. This is a project design, not a claim that Supabase supplies this application session registry. Local-scope sign-out avoids globally terminating other devices. |
| Recovery/confirmation | [PKCE documentation](https://supabase.com/docs/guides/auth/sessions/pkce-flow) | The initiating verifier/browser dependency and failed-flow recovery action are consistent with the provider flow. Restricted recovery-only application permissions are StudyBuddy responsibilities and must be tested. |
| Postgres isolation and transactions | [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [database functions](https://supabase.com/docs/guides/database/functions) | User JWT context, RLS and security-invoker transactional RPCs fit. Ownership policies and execution/table grants are required implementations, not effects automatically conferred by choosing Supabase. Privileged service-role use is excluded from ordinary document operations. |
| Private files | [Storage policies](https://supabase.com/docs/guides/storage/security/access-control) | Storage object RLS and user-scoped credentials are supported. Ready-state policies and backend streaming are project implementation decisions. The document correctly avoids claiming a database/storage atomic transaction. |

## Findings

1. **Low — historical rationale reads as current proposal.** `research-notes.md` has a current finalization section, but its later “Proposed trade-offs” still says hidden answers and the layered monolith are proposals. Label that section historical or update its status wording so builders do not misread settled decisions. No behavior change required.

2. **Implementation gate — isolate overlapping PKCE attempts.** Supabase documents that a later flow can overwrite a stored verifier in a shared client. The spine's per-flow pre-auth registry is appropriate, but the auth story must verify the selected Python SDK actually stores each attempt's verifier independently. Include two concurrent recovery/confirmation attempts and backend-restart tests. This is a compatibility/implementation obligation, not evidence that the chosen pattern is impossible.

## Boundaries

Render remains a candidate, with plan, region, email delivery, quotas and cost checks deferred before provisioning. AI provider/model/API and real-document quality remain separate milestone gates. No claim that the demo proves live auth, owner isolation, durable saving or genuine AI was found in the reviewed contract.
