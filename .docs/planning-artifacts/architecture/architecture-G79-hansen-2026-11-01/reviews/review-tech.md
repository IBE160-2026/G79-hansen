# Architecture technology review

Reviewed: 2026-11-10. Scope: ARCHITECTURE-SPINE.md and research-notes.md. Independent documentation verification only; no package installation, compatibility test, account creation or deployment.

## Verdict

The named framework, PDF candidate and managed-service capabilities have current primary-source evidence. Proposed versions are explicitly observations rather than tested dependency pins. The draft is suitable for discussion; no fabricated package version or claim of completed deployment was found. Two integration details should be made explicit before implementation contracts are treated as final.

## Verified evidence

| Technology or claim | Verification |
| --- | --- |
| FastAPI 0.162.4 | The [maintainer package release](https://pypi.org/project/fastapi/0.162.4/) exists, dated 10 November 2026; metadata requires Python >=3.10. This supports the proposed seed, not a claim that all transitive dependencies have been tested with the local runtime. |
| pypdf 7.0.1 | The [maintainer package release](https://pypi.org/project/pypdf/7.0.1/) exists, dated 10 November 2026, requiring Python >=3.10. The parent checked the official per-page extraction guide. The draft correctly treats extraction fit and resource limits as experiment-dependent and excludes OCR. |
| Python 3.13.7 | Parent recorded the exact local executable's --version output. The draft does not mistake this observed patch for the latest secure deployment patch. |
| Supabase email/password and recovery | [Official password documentation](https://supabase.com/docs/guides/auth/passwords) supports signup/login/recovery, configurable confirmation and redirect allowlists. Choosing a server-managed opaque app cookie is a custom design proposal, not an SDK default; the draft labels it accordingly. |
| User verification and RLS | [Python get_user](https://supabase.com/docs/reference/python/auth-getuser), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) and the parent's private Storage checks support provider-managed identity and separate owner policies. User-scoped clients are a deliberate integration rule; policy enforcement still needs real tests. |
| Render FastAPI hosting | [Official deployment guide](https://render.com/docs/deploy-fastapi) supports a Python service running Uvicorn. It does not establish a selected region/plan, availability, sleep behavior or affordable cost. The draft explicitly leaves these open. |
| Minimal starter | The official FastAPI first-steps app is a verified minimal starting point. No starter repository defaults or existing project structure are falsely claimed. |

## Findings

### Medium — make the multi-table transaction mechanism explicit

Location: AD-8 and Structural Seed.

AD-8 requires an atomic database update for document/content/progress, while AD-2 chooses user-scoped Supabase clients. A sequence of independent table requests is not sufficient evidence of that transaction. The draft has not selected how the repository obtains the required boundary.

Fix: propose a migration-defined Postgres function called through one authenticated RPC for the database part of save/update, using invoker privileges and owner checks/RLS, or explicitly choose a direct database transaction path that preserves authenticated ownership. Keep file-storage compensation separate. [Supabase database functions](https://supabase.com/docs/guides/database/functions) documents callable functions and privilege behavior; do not imply the Python client wraps separate requests into one transaction automatically.

### Medium — document the server-managed confirmation/recovery callback exchange

Location: AD-3 and Deferred.

The proposed browser never receives provider tokens, but AD-3 currently names redirect allowlists without stating how email confirmation/recovery returns credentials to the backend-managed session. The official email flow has explicit implicit/PKCE distinctions. Leaving that boundary unstated could lead one unit to implement a browser token flow while another expects only an opaque app cookie.

Fix: explicitly select a server-side authorization-code/PKCE callback mechanism compatible with the chosen SDK during the auth setup story, with verifier/state ownership defined. Until that is validated, mark this as an auth-integration review gate before those stories are finalized rather than claiming a ready-to-code recovery contract. This is not a reason to reject the user-approved Supabase choice. [Official password flow](https://supabase.com/docs/guides/auth/passwords), [server-side advanced guide](https://supabase.com/docs/guides/auth/server-side/advanced-guide).

## Not findings

- Exact SDK/transitive versions remain intentionally deferred to a clean setup and lockfile check; no false installed-version claim exists.
- The in-memory single-worker session registry is a proposed trade-off. Its loss on restart is documented; it does not undermine remote document persistence by itself.
- Render pricing/region and model/provider choice are explicitly unapproved and unprovisioned. They must remain gates before live setup.
- Architecture recommendations such as bounded extraction, structured output and optimistic revisions are proposed design rules, not claims that a library implements them automatically.

Counts: 0 critical, 0 high, 2 medium. No spine edits made.

## Resolution check — 2026-11-10

Both prior findings are resolved in the draft:

- AD-8 now selects versioned authenticated Postgres RPC functions with SECURITY INVOKER, RLS, owner checks, execution restrictions, row locks and revision checks. It explicitly prohibits treating separate REST inserts as one transaction. File compensation remains separate with durable operation state.
- AD-3 now specifies backend PKCE exchange with verifier/state/browser binding, purpose and expiry in the pre-auth registry. It excludes implicit token fragments, makes recovery sessions password-update-only, consumes recovery state and requires normal login afterward. Restart/expired/reused-code handling and the initiating-browser limitation are explicit. Research notes include the corresponding official sources.

No remaining blocker from these two technology findings. This verifies documentation closure, not runtime SDK compatibility or a tested authentication/deployment implementation. Proposed rules remain subject to the user's draft review.
