# Architecture research — 2026-11-10

This file records evidence and proposal rationale, not installation or deployment results.

| Topic | Evidence checked | Outcome |
| --- | --- | --- |
| FastAPI | [Official first steps](https://fastapi.tiangolo.com/tutorial/first-steps/), [static files](https://fastapi.tiangolo.com/tutorial/static-files/), [maintainer package](https://pypi.org/project/fastapi/) | Same application can serve API and static UI. Package release 0.162.4 dated 2026-11-10 observed in release history; compatibility/install not yet tested. |
| Python | Local `python3.13.exe --version` | 3.13.7 observed; not a claim that this is the newest supported patch. Recheck deployment runtime before binding production version. |
| Supabase Auth | [Password flow](https://supabase.com/docs/guides/auth/passwords), [JWT guidance](https://supabase.com/docs/guides/auth/jwts), [Python get_user](https://supabase.com/docs/reference/python/auth-getuser) | Use provider-managed signup/recovery, validate identity rather than trusting decoded/client-supplied claims. Hosted email confirmation defaults require explicit redirect/email configuration. |
| Private persistence | [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Storage access](https://supabase.com/docs/guides/storage/security/access-control), [private buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals) | Separate table and object policies are required. Selecting the service does not create those policies; ordinary data calls should run as the user, not a policy-bypassing service role. |
| PDF candidate | [pypdf maintainer package](https://pypi.org/project/pypdf/), [extraction guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | 7.0.1 observed, dated 2026-11-10. Per-page text extraction fits the intended experiment; it does not add OCR. Complex content streams can consume excessive memory, so page/text counts alone are insufficient resource controls. |
| Hosting candidate | [Render FastAPI guide](https://render.com/docs/deploy-fastapi) | Python web service supports the proposed app. Candidate only; pricing, sleep/availability behavior, region and email arrangements not checked or selected. No account/service created. |
| Auth callbacks | [PKCE flow](https://supabase.com/docs/guides/auth/sessions/pkce-flow), [Python code exchange](https://supabase.com/docs/reference/python/auth-exchangecodeforsession) | Backend code exchange requires the initiating verifier/browser context. Draft chooses one code flow with restricted recovery-purpose application session rather than mixing browser implicit tokens with backend cookies. |
| Database transactions | [Database functions](https://supabase.com/docs/guides/database/functions) | Versioned Postgres RPC functions provide the transaction boundary for multi-row changes. SECURITY INVOKER, RLS, execution grants and row locks must be designed and tested, not assumed from separate REST calls. |

## Proposed trade-offs

- One layered monolith gives one deployable and shared contracts while keeping extraction/model/storage replaceable. This is a recommendation within the authorized draft.
- A backend-managed opaque session hides provider credentials from browser JavaScript and gives immediate application logout. Initial in-memory session storage requires one worker/instance and re-login after restart; the saved documents remain in Supabase. Scaling requires a shared session store and a new reviewed decision.
- Automatic progress writes for saved content satisfy resumption without making upload/generation auto-save. Optimistic revision checks prevent silent stale-device overwrite. Unsaved source/results remain unsaved.
- Starting answers hidden on reopen is a proposal to avoid exposing answers before practice; restoring positions is already required. Tab switches continue to preserve revealed state during the current visit.
- Database and object storage are not one transaction. Explicit operation states, idempotency and retry are needed to avoid false save/delete success.
- The user asked for proposed choices for the remaining areas. Render and pypdf are researched recommendations; model/provider choice remains a bounded open decision because no API key, cost ceiling or real-document evaluation is available.
