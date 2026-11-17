# Private document library — acceptance, 17 November 2026

Story/spec: `spec-3-2-open-your-private-document-library.md`.

**Current status:** active at `http://127.0.0.1:8000/workspace`, worker14736.
The user's “kjør neste steg” continued the agreed feature in the existing test
project. The implementation handoff stayed local; the parent installed its two
necessary invoker read RPCs after local verification/review. Hosted version
**20261117182650** matches local migration20261117175525, UTF-8/LF SHA-256
`6217a7d409f163f68f816368080af7074f9b266e5394f152c09d041b601e16b8`.

**Final:** Python74; library browser21; Save25/source28; SQL23+23; local provider17;
**hosted25 and normal-server34 passed**. Hosted checks include exact source/bundle,
original bytes, foreign-owner/stale-session denial, actual synthetic file Save,
replacement and registered deletion acknowledgment. Normal checks prove live
routes/private headers, two real logins/library reads and owner isolation.
Real model ledgers remained byte-identical. The final run's two generations used an
injected model and temporary test ledger; **zero real inference/new accounts**.

Focused edge-case/test-gap review yielded six direct corrections, all verified:
reload sequence/version guards, immediate Save availability on Back, accurate
helper text and ungenerated/malformed response regression coverage. The forced-
finding review layer was omitted per the student's lean-work preference.
The first hosted harness assumed a leftover file existed, then reused a workspace
command during replacement. Those test preconditions were corrected; product
code correctly rejected the stale command. The complete final run passed.
An earlier controlled fixture keeps its registered cleanup record in ignored
`hosted-library-fixture-before-retry.json`. Physical/backups purge is not inferred.
Hosted advisors report only the existing Auth password-leak-protection warning.

Implemented Norwegian Mine dokumenter with loading/empty/error/ready states,
50-row UUID keyset pagination, title/date and independent position ordinals and
totals. Owner-ready metadata contains no learning content or object keys. Open
reuses exact reload, restores source/settings/all sections/positions with answers
hidden, and grants no generation receipt. Edits use normal extraction. Listing,
Back, Cancel and failed opens retain the active draft, selected file and revealed
answers. Unsaved replacement requires an inline confirmation.

Original files are proxied through FastAPI and fresh user-JWT S3 reads, bounded
to 10 MiB and the existing operation deadline, with exact size/SHA-256 checking.
The service rechecks the current ready descriptor after reading; the API rechecks
the live session before returning a no-store attachment. No signed URL/key is
returned. Downloaded bytes already on a device cannot be recalled. Session and
workspace epochs fence obsolete list/open/download replies and clear private UI
on access end. Pending Save recovery stays separate.

## Executed local evidence

| Check | Result |
|---|---|
| `uv run pytest tests/test_documents.py tests/test_library.py tests/test_save_acceptance_tools.py -q` | 74 passed; one existing Starlette/httpx deprecation warning |
| `node tests/browser-library.cjs` | 21 final scenarios passed after focused review |
| `node tests/browser-documents.cjs` | All 25 existing Save scenarios passed, adjusted to confirm explicit unsaved reload |
| `supabase test db supabase/tests/library_protocol.test.sql` | 23 pgTAP assertions passed |
| `supabase test db supabase/tests/save_protocol.test.sql` | 23 existing pgTAP assertions passed |
| `SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/library_provider_acceptance.py` | 17 actual local provider checks passed |
| `supabase db lint --schema public,studybuddy --level warning --fail-on warning` | No schema errors found |
| `node --check app/static/workspace.js`; `git diff --check` | Passed; existing LF/CRLF notices only |

CLI 3.1.0 created `20261117175525_open_private_document_library.sql`; migration
up explicitly targeted isolated `studybuddy-save-local` on local port 54422.
No tables or policies were added/relaxed. New functions use SECURITY INVOKER,
fixed empty search_path, owner/ready predicates, the existing backend gate, and
authenticated-only EXECUTE. Pagination follows the existing owner/document UUID
index. Actual RLS tests prove foreign-owner metadata/content/descriptor denial.

The provider checks prove exact reopened snapshots, exact original bytes,
post-read service recheck, direct REST denial after S3 reads, and fresh S3 denial
after lifecycle=deleting, gate retirement and file supersession. The focused
local harness uses 15-second HTTP read headroom and 45-second overall test
budgets; production transport deadlines are unchanged. All model ports were
synthetic: zero inference/hosted calls.

Browser coverage includes empty/retry, safe hostile-title text, keyboard focus,
cancel/failed-open preservation, exact restoration, hidden answers, restart and
fresh-owner isolation, pagination, late list/open/download replies, selected-file
preservation, narrow viewport and 200% reflow, plus no browser persistence.
Ignored full logs are in `test-results/library-{python,browser,save-browser,provider-focused}.log`.

## Remaining gates and observations

The local implementation handoff and parent-hosted activation are complete,
with exact executed evidence recorded above.
Earlier email/link, physical-file retention/deletion/backup and two-device hosted
acceptance gates remain unchanged. Progress autosync and deletion are later stories.

Two earlier broad Save provider reruns stopped with DocumentFailure at different
stages: after pending signed-URL denial (S3 verify), then after foreign internal
verification denial (verified/commit). The second run had already passed fresh
S3 authorization and integrity verification. Their cause was not established;
no production deadlines were changed and the broad suite was not repeatedly
rerun. The focused library provider run above passed with local harness headroom.
Historical logs: `test-results/library-provider.log` contains the last broad
failure; `test-results/library-provider-focused.log` contains the successful run.
Do not treat this as a newly completed broad Save-provider acceptance result.

Unrelated inaccessible content-evaluation evidence files were preserved.
