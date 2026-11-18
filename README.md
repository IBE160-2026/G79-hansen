# G79 — Gruppe123

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Kjør studiedemoen lokalt

Demoen er én FastAPI-applikasjon med vanlig HTML, CSS og JavaScript. Ingen API-nøkler, kontoer eller skytjenester er nødvendige. Installer [uv](https://docs.astral.sh/uv/getting-started/installation/) først. Kjør fra repoets rot:

```powershell
uv sync --locked
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Åpne [http://127.0.0.1:8000](http://127.0.0.1:8000). `uv` bruker Python 3.13.7 fra `.python-version` og kan installere denne hvis den mangler. Python-avhengighetene er låst i `uv.lock`. Første oppsett krever internettilgang; selve demoen kjører lokalt uten nettverkstjenester. Stopp serveren med Ctrl+C.

1. Les det faste eksempelet «Hukommelse og aktiv gjenhenting» og trykk **Lag læringsmateriale**.
2. Bytt mellom Sammendrag, Begreper, Flashcards og Quiz. Svar og kildehenvisning vises sammen når du trykker Vis svar / Vis fasit.
3. Bruk Forrige/Neste. Kort og quiz beholder hver sin posisjon og hvilke svar du har vist når du bytter fane.
4. Vis/rediger åpner materialet uten å endre fremdriften. Ny økt tømmer arbeidsflaten; velg eksempelet på nytt for å starte igjen.

## API og avgrensning for demoen

- `GET /health` returnerer `{"status":"ok","mode":"demo"}`.
- `GET /api/v1/demo/fixture` gir den synlige kilden og de faste innstillingene.
- `POST /api/v1/demo/generate` tar nøyaktig `{"schemaVersion":"1.0","fixtureId":"memory-basics-v1"}` og returnerer alle fire deler samlet. Hver del har stabile element- og kilde-ID-er; hver generering får en ny `generationId`.
- [API-dokumentasjon](http://127.0.0.1:8000/docs) viser kontraktene. Ukjent eksempel, versjon, egne kildefelt, innstillinger og andre ekstra felt gir forståelig HTTP 422 uten behandling eller lagring.

Studiedemoen bruker faste syntetiske eksempeldata på norsk med kort sammendrag. Ingen AI-modell behandler demoteksten. Egen tekst, tekstfil/PDF og språk-/detaljvalg er tilgjengelig i det private arbeidsområdet `/workspace`, med separat aktivert modellkonfigurasjon. Eksplisitt privat Lagre er implementert med separat konfigurasjon og er deaktivert som standard; Mine dokumenter og løpende fremdriftssynkronisering er senere arbeid. Den aktive demotilstanden finnes bare i minnet på den åpne siden og forsvinner ved omlasting. Feil gir eksplisitt prøv-igjen; demoen bytter aldri til et falskt vellykket svar.

Demoen trenger ingen konfigurasjon og gjør ingen Supabase-kall. `/account` tilbyr norsk registrering og innlogging når Supabase er uttrykkelig aktivert og riktig konfigurert; ellers viser siden at innlogging er utilgjengelig. Bare eksplisitte offentlige UI-filer serveres; repositoryfiler og dokumentasjon er ikke statisk tilgjengelige. Den historiske UX-prototypen ligger uendret under `.docs/planning-artifacts/ux-designs/`.

## Konto og Supabase (Story 2.1)

Følg [oppsett og akseptanse for autentisering](.docs/implementation-artifacts/auth-setup.md): organisasjonen **Study Buddy** på **Free**, prosjektet **studybuddy-test** i **Paris (`eu-west-3`)**, med e-postbekreftelse og bare autoriserte teamtestere. Studenten godkjente Paris for det eksisterende testprosjektet 14.11.2026 som en endring fra opprinnelig Frankfurt-plan. Prosjekttilgang og aktiv e-postbekreftelse er kontrollert. Studenten rapporterer vellykket registrering/bekreftelse og separat privat innlogging. To administrative testkontoer bestod 20 HTTP-kontroller, 18 ekstra kontroller av øktlevetid/omstart/fornyelse og 24 kontroller i ekte nettlesere. Tidsgrenser var forkortet bare i en egen testserver; fornyelse brukte ekte Supabase-tokens med instrumentert lokal utløpsmetadata. Gjenværende hosted-tester av e-postbekreftelseslenker og malinspeksjon står åpne før endelig Story 2.1-akseptanse.

Serveren leser `AUTH_ENABLED=true`, `APP_ORIGIN`, `SUPABASE_URL` og `SUPABASE_PUBLISHABLE_KEY` fra prosessmiljøet. `.env.example` er kun dokumentasjon og lastes ikke automatisk. Bruk bare publishable/anon-nøkkel, aldri service_role/secret-nøkkel. Lokal HTTP krever også `AUTH_ALLOW_LOOPBACK_HTTP=true` og loopback-adresse. Andre oppsett krever HTTPS. Manglende/ugyldig konfigurasjon stenger autentiseringen uten å påvirke demoen.

Den lokale ignorerte `.env` kan lastes eksplisitt med `uv run --env-file .env uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1`. Åpne deretter `http://127.0.0.1:8000/account`. Dette aktiverer den konfigurerte innloggingen; vanlig demooppstart laster fortsatt ingen `.env`.

Kjør med **én prosess / én worker**. Tokens og PKCE-forsøk finnes bare i begrenset serverminne; nettleseren får tilfeldige HttpOnly-cookies. Bekreftelsen må åpnes innen ti minutter i nettleseren/profilen der registreringen startet. Økten utløper etter 30 minutter uten aktivitet, senest etter 12 timer, og ved serverrestart. Standarddemoen forblir tilgjengelig uten konto. Lokal utlogging, midlertidig kildekontroll og KI-generering av alle fire læringsdeler er implementert; eksplisitt privat lagring er implementert i Story 3.1 med separat aktivering. Utrulling krever egen godkjenning.

**Glemt passord (Story 2.2)** sender en generell kvittering og bruker en egen PKCE-lenke som må åpnes i samme nettleser/profil innen ti minutter. Lenken gir bare tilgang til skjemaet for nytt passord; den logger deg ikke inn. Et innsendt endringsforsøk bruker opp denne tilgangen før leverandørkallet. Etterpå må du logge inn på vanlig måte. Ved tidsavbrudd kan passordet allerede være endret: prøv innlogging eller be om en ny lenke. Innlogging og gjenoppretting deler maksimalt 1 000 lokale økter; registrering og gjenoppretting deler maksimalt 1 000 ventende forsøk og fire per nettleser. Reell e-post og passordendring krever uttrykkelig testerautorisasjon og er ikke utført av implementasjonstestene. Se [oppsettet](.docs/implementation-artifacts/auth-setup.md) for den ekstra redirect-oppføringen og åpne akseptansepunkter.

## Verifisering

API-/kontrakttester bruker den låste utviklingsgruppen som `uv sync --locked` installerer:

```powershell
uv run pytest
git diff --check
```

For nettlesertester trengs Node.js 22+ og npm. JavaScript-avhengighetene er låst i `package-lock.json`:

```powershell
npm ci
npx playwright install chromium
node tests/browser-demo.cjs
node tests/browser-auth.cjs
```

Testscriptet starter og stopper selv en lokal uvicorn-prosess på en ledig port. Hvis Playwright Chromium mangler, prøver det installert Microsoft Edge. Sett eventuelt `$env:DEMO_BROWSER_CHANNEL = "msedge"` for å velge Edge direkte. `DEMO_BASE_URL` kan peke mot en allerede kjørende lokal demo.

Kontotestene bruker en virkelig nettleser og en lokal server med en adapter som bare finnes i `tests/`. Python-testene kontrollerer også det låste Supabase-SDK-et mot syntetisk HTTP-transport. De dekker sikkerhetsmatrisen, uavhengige nettlesere og PKCE-forsøk, CSRF/Origin, provider-validering, refresh, kapasitets-/utløpsgrenser og trygg håndtering av feil/logging/lagring. Dette er offline verifisering; ekte e-post, bekreftelse og innlogging må gjennomføres separat før live akseptanse kan godkjennes.

Nettlesertestene dekker alle fire deler, kildevisning, separate posisjoner og svar, tastatur/fokus, antall genereringskall, duplikatvern, reset med et forsinket svar som ignorerer kansellering, feil ved første innlasting, semantisk ugyldige svar og eksplisitt retry. Både innlasting og generering har et tidsavbrudd på 15 sekunder som testes med reell ventetid. De kontrollerer horisontal overløp ved 320/390/480 piksler og 200 % layoutzoom og legger skjermbilder i den ignorerte mappen `test-results/`. Dette er automatiserte nettlesersjekker; en full manuell skjermleser- og WCAG-vurdering er ikke gjennomført.

## Lokalt PDF-eksperiment (Story 1.2)

PDF-proben krever Windows med tilgjengelig Job Object-isolasjon. Installer den valgfrie,
låste eksperimentgruppen og kjør fra repoets rot:

```powershell
uv sync --locked --group pdf-experiment
uv run --group pdf-experiment pytest
uv run --group pdf-experiment python scripts/pdf_probe.py --help
```

Lag en syntetisk PDF i den ignorerte testmappen og prøv CLI-en:

```powershell
New-Item -ItemType Directory -Force test-results | Out-Null
uv run --group pdf-experiment python tests/pdf_fixtures.py test-results/synthetic.pdf
uv run --group pdf-experiment python scripts/pdf_probe.py test-results/synthetic.pdf
```

JSON viser status, antall, opprinnelige sidenumre, dekningsvarsel og ressursmålinger.
Kildetekst, filnavn og parserfeil vises aldri. Avvisning gir exit-kode 1. Ved import
gir `scripts.pdf_probe.probe_pdf(path)` og `probe_stream(binary_stream)` også lesbare
kildeenheter i minnet; disse skal ikke logges. Enheten `pdf-page-3` viser fysisk side 3,
selv om side 2 er blank. Blanke sider og bildesider blir oppgitt som ulesbare.

Grensene er 40 fysiske sider, 30 000 Unicode-kodepunkter etter normalisering av
linjeskift, 10 MiB input, 10 sekunder arbeidertid og 512 MiB forpliktet arbeiderminne.
Overskridelser avvises uten avkorting eller delvis aksept. Manglende minneisolasjon
gir `isolation_unavailable`; Linux/macOS støttes foreløpig ikke. Eksperimenttestene
er valgfrie og hoppes over hvis gruppen ikke er installert; `uv run pytest` fortsetter
å kjøre demoens tester.

Se [målerapport og begrensninger](.docs/implementation-artifacts/pdf-experiment.md).
Bare syntetiske PDF-er er testet. Ingen OCR eller tolkning av bilder/tabeller inngår,
og krypterte dokumenter avvises. Dette er lokal gjennomførbarhetstesting;
applikasjonsintegrasjon tilhører Story 2.4. Målplattformen må verifiseres før hosting.
Story 1.1 venter fortsatt på studentens gjennomgang.

## Avslutning av tilgang (Story 2.3)

Story 2.3 adds browser-local **Logg ut** for normal and password-recovery access.
`POST /api/v1/auth/logout` requires the existing Origin/CSRF protection and an
empty JSON object. Local sessions, recovery grants and pending attempts end
atomically; the response deletes request-supplied session cookie generations before best-effort provider
revocation with explicit `local` scope. Provider failure never restores local
access or ends a different browser's session, including the same account.
Revocation admits at most 16 batches without a queue or retry, with one shared
ten-second cooperative deadline per batch and a separate worker limiter. User JWTs are sent directly to the
SDK logout endpoint; logout never refreshes tokens or uses a privileged key.

Status observation does not renew the 30-minute idle / 12-hour absolute maxima.
Normal and restricted status include bounded `expiresInSeconds`; the account
page clears its display at that deadline and checks status every 30 seconds
while visible, on focus and on page restoration. Restart requires fresh login.
Sibling tabs reconcile secret-free termination signals against server status;
old tab timers cannot end a newer login. Lifetime timing includes response delay,
and passive observations preserve forms/focus. Failed logout retains its intent
and retries the protected POST. Each opaque HttpOnly session cookie has its own
generation name, so delayed logout headers cannot delete a newer login cookie.
Story 2.3 introduced no document persistence; explicit Save is added in Story 3.1 below.
Review corrections passed 243 Python tests (one
unchanged optional PDF skip), 33 auth-browser scenarios and 11 demo scenarios.
A separate real-Supabase run passed 25 checks of logout, same-account isolation,
refresh and restart; restricted grants/deadline metadata and revoke failure were
instrumented locally. See [precise acceptance limits](.docs/implementation-artifacts/auth-setup.md#story-23-review-completion--2026-11-15).
Remaining email/recovery-link acceptance is kept separate.

## Eget materiale (Story 2.4)

Åpne `/workspace` etter vanlig innlogging for å kontrollere innlimt tekst,
UTF-8-tekstfil eller tekstbasert PDF. Forhåndsvisningen viser avsnitt eller
opprinnelige fysiske sider og forklarer delvis PDF-dekning. Grensene er
30 000 Unicode-kodepunkter, 40 PDF-sider og 10 MiB per fil; overskridelse
avviser hele kilden. PDF krever den kontrollerte Windows-isolasjonen.

Materialet behandles midlertidig. Endret kilde/innstilling forkaster gammel
forhåndsvisning, og utlogging/utløp/ny innlogging tømmer privat innhold.
KI-generering er tilgjengelig som beskrevet nedenfor; eksplisitt privat lagring krever oppsettet for Story 3.1. Den faste demoen på `/` beholdes.
Kjør `node tests/browser-sources.cjs` for kildeflyten, i tillegg til de øvrige
testene. Se [API, testkommandoer og akseptansegrenser](.docs/implementation-artifacts/source-acceptance.md).

## Medlemmer

- Fredrik Fladmark Hansen

## Private learning generation (Story 2.5)

`/workspace` now has **Lag læringsmateriale**.
The action checks the current source when necessary, then requests summary,
concepts, flashcards and quiz together. The optional source preview remains
available. Unsaved results and selected files exist only in page memory.
Explicit private Save is implemented in Story 3.1 below and disabled by default;
the full library remains Story 3.2. Editing material/settings, reset,
session changes and page exit clear the private result. Technical errors retain
the draft/file/settings and offer explicit retry. Practice navigation and reveal
controls do not call the model.

The fixed demo remains credential-free. Private generation is disabled by
default and has no demo fallback. Enable only after the approved model/data/cost
setup by putting `MODEL_ENABLED=true`, `OPENAI_API_KEY` and `MODEL_BUDGET_PATH`
in the server process environment (see `.env.example`). The application does not
automatically read `.env`. Use only nonsensitive material you are permitted to
send to OpenAI globally. Requests use `gpt-6-luna`, Standard, reasoning `none`,
`store:false` and explicit cache mode without breakpoints. No training opt-in
is enabled; ordinary provider abuse retention is normally up to 30 days, with
exceptions. This is separate from the application's transient storage boundary.

Initialize the content-free local USD 5 lifetime budget ledger **once**, after
approval; never reset or delete an existing ledger to restore allowance:

```powershell
uv run python -m scripts.model_budget init .model-budget.json
uv run python -m scripts.model_budget status .model-budget.json
```

Each dispatch durably reserves USD 0.05 before any network write. Missing,
corrupt, locked, blocked or exhausted ledgers refuse dispatch. Uncertain calls
keep their reservation across restart. This ledger covers this app only, not
other clients using the credential, provider prices, tax or purchases. No
purchase, account, funding or hosted setting is automated.

Unexpected reported usage durably creates a content-free `.blocked` sidecar,
even when another instance owns the ledger lock. Preserve that marker and the
ledger; neither may be removed or reset to restore allowance. All four approved
automated live smoke calls have been executed; their allowance is exhausted.
See the acceptance record for the unchanged historical measurements. Review
corrections use synthetic transports only.

Generation admits one request per session and two globally without a queue or
retry. Its 60-second server deadline includes body/preflight/validation;
extraction is a separately bounded phase. The browser waits at most 70 seconds
after extraction. Provider request/response envelopes are capped at 256 KiB,
output at 8,000 tokens and the private generation protocol at 2 MiB. Unsolicited
compressed provider responses are rejected before decompression. A cancelled
browser wait cannot guarantee the provider stopped billing.

Signed source proofs bind the exact accepted source/settings/coverage/file
hash. Signed generation receipts bind canonical source/settings/bundle hashes
to the current owner, a non-authorizing session binding and ordered workspace
command. Source text, generated content, receipts, credentials and source hashes
are never persisted in the budget ledger. Workspace authority stores metadata
only (at most eight workspaces per session), uses the auth-then-workspace mutex
order and is removed when access ends. Signature validity alone cannot authorize
a superseded result. Story 3.1 coordinates admission with invalidation using an
owned asynchronous workspace gate; no authentication/global lock spans network IO.

Run `uv run --group pdf-experiment pytest`, `node tests/browser-sources.cjs`,
`node tests/browser-auth.cjs`, `node tests/browser-demo.cjs` and `git diff --check`.
The opt-in `scripts.generation_smoke` runner makes at most four automated
synthetic calls over the same ledger's lifetime, including failed calls; it
never initializes the ledger, retries or prints source/output/credentials.
See [the generation acceptance record](.docs/implementation-artifacts/generation-acceptance.md)
for executed checks and the separate Story 2.6 quality/hosting gates.

## Controlled content evaluation (Story 2.6)

The [registered corpus and semantic rubric](.docs/implementation-artifacts/content-evaluation.md)
define three original synthetic documents and two negative cases. The runner
accepts only cases A–E. Default preflight uses production extraction and request
validation offline; it never reads model configuration or budget/grant files:

```powershell
uv run --group pdf-experiment python -m scripts.content_evaluation
uv run --group pdf-experiment pytest tests/test_content_evaluation.py tests/test_generation.py -q
uv run --group pdf-experiment python -m scripts.content_evaluation --register
```

Registration atomically publishes a complete fingerprinted directory beneath
`.docs/implementation-artifacts/content-evaluation-evidence/`, containing fixed
source units, settings, fifteen concept/location expectations, code/prompt hashes,
exact visible PDF lines, the immutable acceptance-rubric hash and a readable
ordinary-font `source-c.pdf`. Mutable status/results are excluded from that rubric
hash. Registration stages both files in an owned temporary directory, flushes
them, and publishes without replacing an existing registration. A failed staging
attempt cleans only its own temporary directory and can be retried offline.
Render and inspect all five physical pages and compare those lines before inference; pages
2 and 4 must be blank. Commit/fingerprint this registration before any live case.
A changed implementation requires a new matching registration, while the frozen
corpus fingerprint remains separately traceable.

After the recorded approval, initialize the separate eight-attempt grant **once**.
This exclusively creates the fixed ignored `.model-budget-evaluation-2-6.json`;
it cannot reset an existing file. The existing global USD 5 ledger must already
exist. A live run additionally requires the same process model configuration as
generation; use the existing approved configuration, with no credentials in
command arguments. Execute one explicitly selected case per invocation:

```powershell
uv run python -m scripts.content_evaluation --initialize-grant
uv run --env-file .env --group pdf-experiment python -m scripts.content_evaluation --live --case A
uv run --env-file .env --group pdf-experiment python -m scripts.content_evaluation --live --case A --phase recheck
```

The final command is only for an approved, needed recheck. There are eight total
attempts across restarts, including failed or uncertain attempts. Each consumes
the evaluation grant durably before reserving USD 0.05 in the existing global
ledger. No reservation is refunded, no retry is automatic, and a concurrent
runner fails immediately. An existing destination evidence file is rejected
under the grant lock before either allowance is consumed or a provider attempt
starts. The original four-smoke counter stays unchanged and
cannot be reused. Each attempt writes a new synthetic evidence file; numeric
errors omit provider messages and raw envelopes. JSON evidence is fully flushed
to an owned temporary file, then atomically published without replacement, using
Windows write-through or POSIX directory synchronization. Registration/PDF reads
are bounded before allocation. Error codes are 1 configuration,
2 grant/lock, 3 global reservation, 4 provider/usage, 5 output structure/reference
identity, 6 evidence persistence, 7 registration, 8 case selection, 9 deadline,
10 internal/other safe stop, and 11 explicit cancellation. Attempt evidence records
`globalReservationCompleted` and `providerAttemptStarted` booleans. These describe
local completion/start phases only; neither proves upstream receipt or billing.
For deadline code 9 they distinguish a stop before the provider attempt from a
deadline during that attempt. Failed/uncertain dispatch and cancellation retain
all consumed allowances. The five historical outputs/assessments keep their
original metadata and registration; these added fields apply to future attempts.

Structural validation establishes reference identity only. Audit every returned
item for factual support and substantive reference correctness; score each
registered concept semantically, retaining unsupported claims, wrong references
and omissions separately. Preserve initial failures and link fixes, regressions
and rechecks. Offline integrity tests validate historical observation hashes,
complete item/reference enumeration, exact excerpts and coverage identity links;
they establish traceability and do not judge semantic correctness.
A shared instruction change needs final evidence for all five
cases. Exhausted allowance or unresolved failures leave acceptance incomplete.
Passing this controlled corpus establishes its observed synthetic results only;
arbitrary course documents, complex PDF reading order/OCR, deployed isolation,
screen-reader assessment and earlier real-email gates remain separate.

## Explicit private Save (Story 3.1)

Storage verification update, 17 November 2026: authenticated REST downloads can
cache a successful internal read by user JWT and bypass later backend/lifecycle
checks. Original-file verification now uses uncached S3 session-token reads with
the same user JWT, owner RLS and backend capability. It requires
`SUPABASE_S3_REGION`, `SUPABASE_S3_KEY_ID` (project reference) and
`SUPABASE_S3_ANON_KEY` (legacy public anon key; never a privileged S3/service key).
The new read-policy migration must be approved and applied before activation.
See the current status at the top of the Save acceptance record.
The existing test setup was approved and activated on 17 November: 32 synthetic
hosted checks and 30 normal-server checks passed without real model calls. The
local app is available at `http://127.0.0.1:8000/workspace`; fresh login is required.

After generating material, **Lagre** saves the validated source, settings, four
learning sections, optional original file and the independent current flashcard
and quiz positions. The optional title accepts 160 Unicode code points. Save
makes no model call. Navigating practice does not save again; progress sync is
Story 3.3. Edits keep the saved document as the explicit replacement target;
**Ny økt** detaches that target without deleting data. Revision conflicts offer
**Hent lagret versjon** or **Lagre som nytt** and preserve the unsaved draft.

Save is disabled by default. It requires the migration, private bucket policies,
an administrator-installed verifier hash, `SAVE_ENABLED=true`, and the ignored
server capability file named by `SAVE_BACKEND_KEY_PATH`. The application never
loads `.env` automatically and uses user JWTs, never a service key, for ordinary
document/Storage work. The migration and exact hosted approval boundary are in
[the Save acceptance record](.docs/implementation-artifacts/save-acceptance.md).
No hosted migration/configuration is authorized by local implementation approval.

After approval, `uv run python -m scripts.save_backend_key` exclusively creates
the ignored `.save-backend-key` file with restricted permissions. It refuses an
existing/unignored destination and prints only `keyId` and the SHA-256 verifier.
Install only that verifier in `studybuddy.backend_verifiers` as administration.
Never put the raw capability in SQL, arguments, browser code or logs. Key rotation
changes current backend authorization without changing admitted operation IDs.

An immutable operation is durably admitted before any upload. Exact retries
return the recorded outcome before checking an old receipt/revision. A pending
panel after fresh login identifies pending same-owner operations by title and
admission/expiry times. Exact recovery lasts seven days using the stored snapshot
and matching original bytes when needed. Confirmed completed outcomes remain
discoverable for seven days after completion, including a lost successful reply.
At expiry, upload/commit is rejected exactly. A minute-by-minute administrator
database job erases overdue staging/title independently of owner login; physical
staging purge follows the next successful bounded maintenance batch. Scheduler
failure or backlog delays erasure and fails retention acceptance. Operators must
check `cron.job`, `cron.job_run_details` and
`studybuddy.expiry_maintenance_health`; see the acceptance record for health SQL.
`uv run python -m scripts.save_cleanup` asks for a fresh user JWT using a hidden
prompt, validates that identity, expires owner staging and retries registered
cleanup; it does not use or create accounts. Registered uncertain writes stay
discoverable. Object-free terminal operations report `cleanup_complete` and leave
content-free tombstones; registered file cleanup remains pending without physical
provider quiescence evidence. Ready Save and cleanup status are separate. Database
erasure does not establish removal from backups or physical blob storage; those
remain separate real-file acceptance gates.

Run `uv run pytest`, `node tests/browser-documents.cjs` and the three existing
browser suites. Injected-port tests exercise application lifecycle/failures;
`supabase/tests/save_protocol.test.sql` and the isolated local provider runner
exercise actual transactions/RLS/Storage. Their exact executed evidence and
remaining hosted/real-file/provider retention gates belong in the acceptance record.

**Mine dokumenter** lists only your ready saved documents, fifty per page, with
title, save date and the independently saved card/quiz positions. Listing and
returning preserve the active draft. Opening asks before replacing unsaved work,
restores the exact saved source/settings/four sections with answers hidden, and
makes no model call or generation receipt. Editing then uses normal extraction.
**Last ned originalfil** verifies the saved original's size and SHA-256 through
an authenticated, uncached user-JWT S3 read and returns an attachment. The browser
receives neither object keys nor signed URLs. Downloaded files remain on the
device after logout. New session clears only the workspace.

Mine dokumenter is active in the existing test setup after local and hosted
verification on 17 November 2026. Log in again after the local server restart.
Run `uv run pytest tests/test_library.py tests/test_documents.py
tests/test_save_acceptance_tools.py -q`, `node tests/browser-library.cjs`, and
the existing Save browser suite. Real local checks use
`SAVE_TEST_WSL_DISTRO=SUREUbuntu` with
`uv run python tests/library_provider_acceptance.py` and
`supabase/tests/library_protocol.test.sql`. See
[library acceptance](.docs/implementation-artifacts/library-acceptance.md) for
executed results and remaining release/retention limits.

Saved practice navigation now synchronizes the independent card/quiz positions.
Only acknowledged progress is guaranteed after leaving. A stale view reports
**Fremdriften er endret på en annen enhet** and requires **Hent siste fremdrift**;
fetching hides answers. An uncertain write retries its exact mutation once, then
offers explicit retry/refetch. Editing or generating new material requires an
explicit content Save before progress sync resumes. Opening a newer saved
generation requires reopening the document. No inference occurs during sync.

Focused checks: `uv run --locked pytest tests/test_progress.py -q`,
`node tests/browser-progress.cjs`, `supabase/tests/progress_protocol.test.sql`, and
the isolated local `tests/progress_provider_acceptance.py` runner with
`SAVE_TEST_WSL_DISTRO=SUREUbuntu`. See
[progress acceptance](.docs/implementation-artifacts/progress-acceptance.md)
for exact executed results and remaining integration limits.

Local Story 3.4 adds **Slett** in Mine dokumenter: a named confirmation includes
the source, learning material and progress; **Avbryt** changes nothing. Confirmed
deletion closes access immediately, clears the active saved workspace and only
reports success after verified object cleanup and transactional data removal.
Failures remain under pending deletions with **Prøv sletting igjen**, including
after fresh login. Unknown upload attempts stay tracked until reconciled.

The CLI-created deletion migration is local-only and awaits separate hosted
approval. Focused checks are `uv run pytest tests/test_deletion.py -q`,
`node tests/browser-deletion.cjs`, `supabase/tests/deletion_protocol.test.sql` and
`SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_provider_acceptance.py`.
See [deletion acceptance](.docs/implementation-artifacts/deletion-acceptance.md)
for executed evidence, seven-day content-free retry retention and the remaining
backup/physical-retention gates before real files.
